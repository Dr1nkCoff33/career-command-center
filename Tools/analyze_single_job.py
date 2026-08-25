#!/usr/bin/env python3
"""
Analyze a single job posting against a resume using Firecrawl and Claude AI.
"""

import os
import sys
import json
from datetime import datetime
from firecrawl_job_scraper import FirecrawlJobScraper, JobPostingExtractor
from job_analyzer_cli import ClaudeAnalyzer

def analyze_single_job(job_url: str, resume_path: str):
    """Analyze a single job posting against a resume."""
    
    firecrawl_key = os.environ.get('FIRECRAWL_API_KEY')
    claude_key = os.environ.get('CLAUDE_API_KEY')

    if not firecrawl_key or not claude_key:
        print('Error: FIRECRAWL_API_KEY and CLAUDE_API_KEY environment variables are required.')
        sys.exit(1)
    
    scraper = FirecrawlJobScraper(firecrawl_key)
    claude = ClaudeAnalyzer(claude_key)
    
    print(f"🚀 Single Job Analysis Tool")
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
        
        # Analyze with Claude
        print("\n🤖 Analyzing job fit with Claude AI...")
        fit_analysis = claude.analyze_job_fit(job_description, resume_text)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 ANALYSIS RESULTS")
        print("=" * 60)
        
        if fit_analysis:
            print(f"\n🎯 Match Score: {fit_analysis.get('match_percentage', 'N/A')}%")
            
            strengths = fit_analysis.get('key_strengths', [])
            if strengths:
                print("\n✅ Key Strengths:")
                for strength in strengths:
                    print(f"  • {strength}")
            
            gaps = fit_analysis.get('critical_gaps', [])
            if gaps:
                print("\n⚠️  Critical Gaps:")
                for gap in gaps:
                    print(f"  • {gap}")
            
            suggestions = fit_analysis.get('specific_suggestions', [])
            if suggestions:
                print("\n💡 Resume Improvement Suggestions:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            
            keywords = fit_analysis.get('missing_keywords', [])
            if keywords:
                print("\n🔑 Missing Keywords:")
                print(f"  {', '.join(keywords)}")
        
        # Generate tailored bullets
        print("\n✍️  Generating tailored resume bullets...")
        requirements = []
        if isinstance(job_content, dict):
            requirements = job_content.get('skills_required', []) or job_content.get('requirements', [])
        
        if not requirements and job_description:
            # Extract requirements from description
            requirements = ["sourcing", "talent acquisition", "recruiting", "candidate pipeline", "diversity hiring"]
        
        tailored_bullets = claude.generate_tailored_content(requirements[:10], resume_text[:500])
        
        if tailored_bullets:
            print("\n📝 Tailored Resume Bullets:")
            for bullet in tailored_bullets:
                if bullet.strip():
                    print(f"  • {bullet.strip()}")
        
        # Save detailed report
        report_file = f"job_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'analysis_date': datetime.now().isoformat(),
            'job_url': job_url,
            'resume_path': resume_path,
            'job_content': job_content,
            'fit_analysis': fit_analysis,
            'tailored_bullets': tailored_bullets
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
    else:
        print("❌ Failed to scrape job posting")
        print("  This might be due to the website's structure or access restrictions")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_single_job.py <job_url> <resume_path>")
        sys.exit(1)
    
    job_url = sys.argv[1]
    resume_path = sys.argv[2]
    
    analyze_single_job(job_url, resume_path)