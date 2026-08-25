#!/usr/bin/env python3
"""
Enhanced version of analyze_single_job.py that integrates BERTopic semantic matching
for improved resume-job alignment analysis.
"""

import os
import sys
import json
from datetime import datetime
from firecrawl_job_scraper import FirecrawlJobScraper, JobPostingExtractor
from job_analyzer_cli import ClaudeAnalyzer
from semantic_matcher import SemanticMatcher, enhance_claude_analysis_with_semantics


def analyze_single_job_enhanced(job_url: str, resume_path: str):
    """Analyze a single job posting against a resume with semantic matching."""
    
    firecrawl_key = os.environ.get('FIRECRAWL_API_KEY')
    claude_key = os.environ.get('CLAUDE_API_KEY')

    if not firecrawl_key or not claude_key:
        print('Error: FIRECRAWL_API_KEY and CLAUDE_API_KEY environment variables are required.')
        sys.exit(1)
    
    scraper = FirecrawlJobScraper(firecrawl_key)
    claude = ClaudeAnalyzer(claude_key)
    semantic_matcher = SemanticMatcher()
    
    print(f"🚀 Enhanced Job Analysis Tool (with BERTopic)")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🔗 Job URL: {job_url}")
    print(f"📄 Resume: {resume_path}")
    
    # Read resume
    print("\n📄 Loading resume...")
    try:
        with open(resume_path, 'r') as f:
            resume_text = f.read()
        print("✅ Resume loaded successfully")
    except Exception as e:
        print(f"❌ Error loading resume: {e}")
        return
    
    # Scrape job posting
    print("\n🔍 Scraping job posting...")
    schema = JobPostingExtractor.get_job_extraction_schema()
    job_data = scraper.scrape_url(job_url, extract_schema=schema)
    
    if not job_data or not job_data.get('success'):
        # Try without schema
        print("  Trying alternative scraping method...")
        job_data = scraper.scrape_url(job_url)
    
    if job_data and job_data.get('success'):
        print("✅ Job posting scraped successfully")
        
        # Extract job description
        job_content = job_data.get('data', {})
        if isinstance(job_content, dict):
            job_description = job_content.get('description', '') or job_content.get('markdown', '') or str(job_content)
        else:
            job_description = str(job_content)
        
        # Semantic Analysis with BERTopic
        print("\n🧠 Performing semantic analysis with BERTopic...")
        semantic_results = semantic_matcher.calculate_comprehensive_match(resume_text, job_description)
        
        # Get keyword recommendations
        keyword_recommendations = semantic_matcher.get_keyword_recommendations(resume_text, job_description)
        semantic_results['keyword_recommendations'] = keyword_recommendations
        
        # Claude Analysis
        print("\n🤖 Analyzing job fit with Claude AI...")
        claude_analysis = claude.analyze_job_fit(job_description, resume_text)
        
        # Enhance Claude analysis with semantic insights
        if claude_analysis:
            fit_analysis = enhance_claude_analysis_with_semantics(claude_analysis, semantic_results)
        else:
            fit_analysis = semantic_results
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 ENHANCED ANALYSIS RESULTS")
        print("=" * 60)
        
        # Show both scores
        print(f"\n🎯 Match Scores:")
        print(f"  • Claude AI Score: {claude_analysis.get('match_percentage', 'N/A')}%")
        print(f"  • Semantic Score: {semantic_results['match_percentage']}%")
        print(f"  • Combined Score: {fit_analysis.get('match_percentage', 'N/A')}%")
        
        # Semantic insights
        print(f"\n🧠 Semantic Analysis:")
        print(f"  • Overall Similarity: {semantic_results['overall_similarity']}%")
        if semantic_results['section_scores']:
            print("  • Section Scores:")
            for section, score in semantic_results['section_scores'].items():
                print(f"    - {section}: {score}%")
        
        # Topic Analysis
        topic_analysis = semantic_results['topic_analysis']
        if topic_analysis['common_topics']:
            print(f"\n📌 Common Topics Found:")
            for topic in topic_analysis['common_topics'][:5]:
                print(f"  • {topic}")
        
        # Original Claude insights
        if isinstance(claude_analysis, dict):
            strengths = claude_analysis.get('key_strengths', [])
            if strengths:
                print("\n✅ Key Strengths:")
                for strength in strengths:
                    print(f"  • {strength}")
            
            gaps = claude_analysis.get('critical_gaps', [])
            if gaps:
                print("\n⚠️  Critical Gaps:")
                for gap in gaps:
                    print(f"  • {gap}")
        
        # Semantic insights
        if semantic_results['semantic_insights']:
            print("\n💡 Semantic Insights:")
            for insight in semantic_results['semantic_insights']:
                print(f"  • {insight}")
        
        # Enhanced keyword recommendations
        all_keywords = set()
        if isinstance(claude_analysis, dict) and 'missing_keywords' in claude_analysis:
            all_keywords.update(claude_analysis['missing_keywords'])
        if keyword_recommendations:
            all_keywords.update(keyword_recommendations)
        
        if all_keywords:
            print("\n🔑 Recommended Keywords to Add:")
            for i, keyword in enumerate(list(all_keywords)[:15], 1):
                print(f"  {i}. {keyword}")
        
        # Improvement suggestions
        if isinstance(claude_analysis, dict):
            suggestions = claude_analysis.get('specific_suggestions', [])
            if suggestions:
                print("\n📝 Resume Improvement Suggestions:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
        
        # Generate tailored bullets
        print("\n✍️  Generating tailored resume bullets...")
        requirements = []
        if isinstance(job_content, dict):
            requirements = job_content.get('skills_required', []) or job_content.get('requirements', [])
        
        if not requirements and job_description:
            # Use semantic topics as requirements
            requirements = topic_analysis['job_topics'][:10]
        
        tailored_bullets = claude.generate_tailored_content(requirements[:10], resume_text[:500])
        
        if tailored_bullets:
            print("\n📝 Tailored Resume Bullets:")
            for bullet in tailored_bullets:
                if bullet.strip():
                    print(f"  • {bullet.strip()}")
        
        # Save enhanced report
        report_file = f"job_analysis_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'analysis_date': datetime.now().isoformat(),
            'job_url': job_url,
            'resume_path': resume_path,
            'job_content': job_content,
            'claude_analysis': claude_analysis,
            'semantic_analysis': semantic_results,
            'combined_analysis': fit_analysis,
            'tailored_bullets': tailored_bullets
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Enhanced report saved to: {report_file}")
        
        # Generate markdown report
        generate_enhanced_markdown_report(report_data)
        
    else:
        print("❌ Failed to scrape job posting")
        print("  This might be due to the website's structure or access restrictions")


def generate_enhanced_markdown_report(report_data: dict):
    """Generate an enhanced markdown report with semantic analysis."""
    
    filename = f"job_analysis_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filename, 'w') as f:
        f.write("# Enhanced Job Analysis Report (with BERTopic)\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Job URL:** {report_data['job_url']}\n")
        f.write(f"**Analysis Method:** Claude AI + BERTopic Semantic Matching\n\n")
        
        # Match scores
        f.write("## 🎯 Match Analysis\n\n")
        claude_analysis = report_data.get('claude_analysis', {})
        semantic_analysis = report_data.get('semantic_analysis', {})
        combined_analysis = report_data.get('combined_analysis', {})
        
        f.write("| Analysis Type | Match Score |\n")
        f.write("|--------------|-------------|\n")
        f.write(f"| Claude AI | {claude_analysis.get('match_percentage', 'N/A')}% |\n")
        f.write(f"| Semantic (BERTopic) | {semantic_analysis.get('match_percentage', 'N/A')}% |\n")
        f.write(f"| **Combined Score** | **{combined_analysis.get('match_percentage', 'N/A')}%** |\n\n")
        
        # Semantic section scores
        if semantic_analysis.get('section_scores'):
            f.write("### Section-Level Semantic Alignment\n\n")
            for section, score in semantic_analysis['section_scores'].items():
                f.write(f"- **{section.replace('_', ' ').title()}:** {score}%\n")
            f.write("\n")
        
        # Topic analysis
        topic_analysis = semantic_analysis.get('topic_analysis', {})
        if topic_analysis:
            f.write("## 📊 Topic Analysis\n\n")
            if topic_analysis.get('common_topics'):
                f.write("### Aligned Topics\n")
                for topic in topic_analysis['common_topics'][:10]:
                    f.write(f"- {topic}\n")
                f.write("\n")
            
            missing_topics = set(topic_analysis.get('job_topics', [])) - set(topic_analysis.get('resume_topics', []))
            if missing_topics:
                f.write("### Missing Topics to Address\n")
                for topic in list(missing_topics)[:10]:
                    f.write(f"- {topic}\n")
                f.write("\n")
        
        # Strengths and gaps
        if isinstance(claude_analysis, dict):
            if claude_analysis.get('key_strengths'):
                f.write("## ✅ Key Strengths\n\n")
                for strength in claude_analysis['key_strengths']:
                    f.write(f"- {strength}\n")
                f.write("\n")
            
            if claude_analysis.get('critical_gaps'):
                f.write("## ⚠️ Critical Gaps\n\n")
                for gap in claude_analysis['critical_gaps']:
                    f.write(f"- {gap}\n")
                f.write("\n")
        
        # Semantic insights
        if semantic_analysis.get('semantic_insights'):
            f.write("## 💡 Semantic Insights\n\n")
            for insight in semantic_analysis['semantic_insights']:
                f.write(f"- {insight}\n")
            f.write("\n")
        
        # Keywords
        all_keywords = set()
        if isinstance(claude_analysis, dict) and 'missing_keywords' in claude_analysis:
            all_keywords.update(claude_analysis['missing_keywords'])
        if semantic_analysis.get('keyword_recommendations'):
            all_keywords.update(semantic_analysis['keyword_recommendations'])
        
        if all_keywords:
            f.write("## 🔑 Keywords to Incorporate\n\n")
            f.write("Add these keywords to improve alignment:\n\n")
            for keyword in list(all_keywords)[:20]:
                f.write(f"- {keyword}\n")
            f.write("\n")
        
        # Tailored bullets
        if report_data.get('tailored_bullets'):
            f.write("## 📝 Tailored Resume Bullets\n\n")
            for bullet in report_data['tailored_bullets']:
                if bullet.strip():
                    f.write(f"• {bullet.strip()}\n")
            f.write("\n")
        
        # Recommendations
        f.write("## 🚀 Next Steps\n\n")
        f.write("1. **Immediate Actions:**\n")
        f.write("   - Add missing keywords throughout your resume\n")
        f.write("   - Incorporate the tailored bullets into relevant experience sections\n")
        f.write("   - Address the critical gaps identified\n\n")
        f.write("2. **Content Optimization:**\n")
        f.write("   - Align your experience descriptions with the job responsibilities\n")
        f.write("   - Emphasize achievements that demonstrate required competencies\n")
        f.write("   - Use industry-specific terminology found in the topic analysis\n\n")
        f.write("3. **Semantic Enhancement:**\n")
        f.write("   - Review sections with low semantic scores\n")
        f.write("   - Incorporate missing topics naturally into your descriptions\n")
        f.write("   - Ensure your skills section uses the same language as the job posting\n")
    
    print(f"\n📄 Enhanced markdown report saved to: {filename}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_single_job_enhanced.py <job_url> <resume_path>")
        sys.exit(1)
    
    job_url = sys.argv[1]
    resume_path = sys.argv[2]
    
    analyze_single_job_enhanced(job_url, resume_path)