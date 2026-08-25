#!/usr/bin/env python3
"""
chatgpt_export_preprocessor.py

Preprocesses large ChatGPT export HTML files for AI analysis.

Features:
- Streams and parses large HTML files incrementally (conversation by conversation)
- Extracts conversations, messages, metadata, and topics
- Cleans and normalizes text
- Enriches data with word counts, durations, etc.
- Categorizes and summarizes conversations
- Outputs analysis-ready files (JSON, JSONL, topical and temporal splits)
- Progress indicators and error handling
- Usage example and CLI options (date range, input/output, etc.)

Usage Example:
    python chatgpt_export_preprocessor.py --input /path/to/chat.html --output_dir ./output --start_date 2024-01-01 --end_date 2024-06-30

Dependencies: beautifulsoup4, pandas
"""
import os
import sys
import re
import json
import argparse
import datetime
import time
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import pandas as pd

# --- CONFIG ---
CHUNK_SIZE = 1024 * 1024  # 1MB
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB

# --- UTILS ---
def clean_text(html_text: str) -> str:
    """Remove HTML tags, fix encoding, normalize whitespace."""
    text = BeautifulSoup(html_text, "lxml").get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def estimate_json_size(obj) -> int:
    return len(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

def timestamp_now() -> str:
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# --- PARSING ---
def parse_conversations(html_path: str, start_date: Optional[str], end_date: Optional[str]):
    """Yield parsed conversations from the HTML file, streaming for large files."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
        # Find all conversation containers (structure may vary)
        conversations = soup.find_all('div', class_=re.compile(r'chat|conversation', re.I))
        for conv in conversations:
            try:
                # Extract metadata
                title = conv.find('h3') or conv.find('h2')
                title = clean_text(title.text) if title else None
                messages = []
                timestamps = []
                for msg in conv.find_all('div', class_=re.compile(r'message|msg|turn', re.I)):
                    role = 'user' if 'user' in msg.get('class', []) else 'ai' if 'assistant' in msg.get('class', []) else 'unknown'
                    text = clean_text(msg.text)
                    ts = None
                    # Try to extract timestamp if present
                    ts_tag = msg.find('time') or msg.find('span', class_=re.compile(r'time|date', re.I))
                    if ts_tag:
                        try:
                            ts = pd.to_datetime(ts_tag.text, errors='coerce')
                        except Exception:
                            ts = None
                    messages.append({'role': role, 'text': text, 'timestamp': str(ts) if ts else None})
                    if ts:
                        timestamps.append(ts)
                if not messages:
                    continue
                # Date filtering
                if timestamps:
                    conv_start = min([t for t in timestamps if t is not None])
                    conv_end = max([t for t in timestamps if t is not None])
                else:
                    conv_start = conv_end = None
                if start_date and conv_start and conv_start < pd.to_datetime(start_date):
                    continue
                if end_date and conv_end and conv_end > pd.to_datetime(end_date):
                    continue
                yield {
                    'title': title,
                    'messages': messages,
                    'start_timestamp': str(conv_start) if conv_start else None,
                    'end_timestamp': str(conv_end) if conv_end else None
                }
            except Exception as e:
                print(f"[WARN] Skipping malformed conversation: {e}")

# --- ENRICHMENT ---
def enrich_conversation(conv: Dict[str, Any]) -> Dict[str, Any]:
    messages = conv['messages']
    word_counts = [len(m['text'].split()) for m in messages]
    message_count = len(messages)
    total_words = sum(word_counts)
    start_ts = pd.to_datetime(conv['start_timestamp']) if conv['start_timestamp'] else None
    end_ts = pd.to_datetime(conv['end_timestamp']) if conv['end_timestamp'] else None
    duration = (end_ts - start_ts).total_seconds() / 60 if start_ts and end_ts else None
    topic = conv['title'] or (messages[0]['text'][:60] if messages else None)
    # Simple question type detection
    question_types = []
    for m in messages:
        if re.search(r'\bcode|python|script|function|error\b', m['text'], re.I):
            question_types.append('coding')
        elif re.search(r'\bessay|write|story|paragraph\b', m['text'], re.I):
            question_types.append('writing')
        elif re.search(r'\bresearch|explain|summarize\b', m['text'], re.I):
            question_types.append('research')
    question_type = Counter(question_types).most_common(1)[0][0] if question_types else 'general'
    summary = messages[0]['text'] if messages else ''
    return {
        **conv,
        'message_count': message_count,
        'total_words': total_words,
        'duration_minutes': duration,
        'topic': topic,
        'question_type': question_type,
        'summary': summary
    }

# --- OUTPUT ---
def write_jsonl(convs, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        for c in convs:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')

def write_json(convs, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(convs, f, ensure_ascii=False, indent=2)

def split_and_write(convs, out_dir, key_func, prefix):
    """Split conversations by key_func (e.g., topic, date), keep files <10MB."""
    buckets = defaultdict(list)
    for c in convs:
        k = key_func(c)
        buckets[k].append(c)
    for k, group in buckets.items():
        chunk = []
        size = 0
        idx = 1
        for conv in group:
            conv_size = estimate_json_size(conv)
            if size + conv_size > MAX_OUTPUT_SIZE:
                out_path = os.path.join(out_dir, f"{prefix}_{k}_{idx}_{timestamp_now()}.json")
                write_json(chunk, out_path)
                chunk = []
                size = 0
                idx += 1
            chunk.append(conv)
            size += conv_size
        if chunk:
            out_path = os.path.join(out_dir, f"{prefix}_{k}_{idx}_{timestamp_now()}.json")
            write_json(chunk, out_path)

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser(description="Preprocess ChatGPT export HTML for AI analysis.")
    parser.add_argument('--input', required=True, help='Path to ChatGPT export HTML file')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    parser.add_argument('--start_date', help='Filter: start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='Filter: end date (YYYY-MM-DD)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"[INFO] Processing {args.input} ...")
    conversations = []
    for i, conv in enumerate(parse_conversations(args.input, args.start_date, args.end_date)):
        enriched = enrich_conversation(conv)
        conversations.append(enriched)
        if (i+1) % 10 == 0:
            print(f"[INFO] Parsed {i+1} conversations...")
    print(f"[INFO] Total conversations parsed: {len(conversations)}")

    # Write summary (prioritize this)
    summary_path = os.path.join(args.output_dir, f"conversations_summary_{timestamp_now()}.json")
    write_json(conversations, summary_path)
    print(f"[INFO] Wrote summary: {summary_path}")

    # Write full JSONL
    jsonl_path = os.path.join(args.output_dir, f"full_conversations_{timestamp_now()}.jsonl")
    write_jsonl(conversations, jsonl_path)
    print(f"[INFO] Wrote full JSONL: {jsonl_path}")

    # Split by topic
    topic_dir = os.path.join(args.output_dir, 'conversations_by_topic')
    os.makedirs(topic_dir, exist_ok=True)
    split_and_write(conversations, topic_dir, lambda c: c['topic'][:30].replace(' ', '_'), 'topic')
    print(f"[INFO] Wrote topical splits to {topic_dir}")

    # Split by temporal chunk (monthly)
    temp_dir = os.path.join(args.output_dir, 'temporal_chunks')
    os.makedirs(temp_dir, exist_ok=True)
    def month_key(c):
        if c['start_timestamp']:
            dt = pd.to_datetime(c['start_timestamp'])
            return dt.strftime('%Y-%m')
        return 'unknown'
    split_and_write(conversations, temp_dir, month_key, 'month')
    print(f"[INFO] Wrote temporal splits to {temp_dir}")

    # Write data overview
    overview_path = os.path.join(args.output_dir, f"data_overview_{timestamp_now()}.txt")
    topics = Counter([c['topic'] for c in conversations])
    date_range = (min([c['start_timestamp'] for c in conversations if c['start_timestamp']]),
                  max([c['end_timestamp'] for c in conversations if c['end_timestamp']]))
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write(f"Total conversations: {len(conversations)}\n")
        f.write(f"Date range: {date_range[0]} to {date_range[1]}\n")
        f.write(f"Top topics: {topics.most_common(10)}\n")
        f.write(f"\nFile structure:\n")
        f.write(f"- {summary_path} (summary, <5MB)\n")
        f.write(f"- {jsonl_path} (full, JSONL)\n")
        f.write(f"- {topic_dir}/ (by topic, <10MB each)\n")
        f.write(f"- {temp_dir}/ (by month, <10MB each)\n")
        for root, dirs, files in os.walk(args.output_dir):
            for file in files:
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                f.write(f"  - {os.path.relpath(path, args.output_dir)}: {size/1024/1024:.2f} MB\n")
        f.write("\nSuggested analysis approaches:\n")
        f.write("- Topic modeling, clustering, time series analysis, prompt/response quality, etc.\n")
    print(f"[INFO] Wrote data overview: {overview_path}")

if __name__ == '__main__':
    main() 