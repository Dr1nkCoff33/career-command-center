#!/usr/bin/env python3
"""
Job Analyzer CLI - Command-line interface for job market analysis
Combines Firecrawl scraping with Claude AI analysis for intelligent resume optimization.
"""

import argparse
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Import our modules
from job_market_analyzer import JobAnalyzer, ResumeOptimizer, JobMarketReport
from firecrawl_job_scraper import FirecrawlJobScraper, JobPostingExtractor, generate_job_market_report


class ClaudeAnalyzer:
    """Use Claude API for intelligent job and resume analysis."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
    def analyze_job_fit(self, job_description: str, resume_text: str) -> Dict:
        """Use Claude to analyze how well a resume fits a job description."""
        prompt = f"""Analyze how well this resume matches the job description. 
        
Job Description:
{job_description}

Resume:
{resume_text}

Please provide:
1. Match percentage (0-100%)
2. Key strengths that align with the job
3. Critical gaps that need to be addressed
4. Specific suggestions to improve the resume for this role
5. Keywords missing from the resume that appear in the job description

Format your response as JSON."""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            if response.status_code == 200:
                content = response.json()['content'][0]['text']
                # Parse JSON response
                return json.loads(content)
            else:
                print(f"Claude API error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return {}
    
    def generate_tailored_content(self, job_requirements: List[str], experience: str) -> List[str]:
        """Generate tailored resume bullets based on job requirements."""
        prompt = f"""Based on these job requirements, generate 5 tailored resume bullet points 
        that showcase relevant experience.
        
Job Requirements:
{json.dumps(job_requirements, indent=2)}

Current Experience Context:
{experience}

Generate bullet points that:
1. Use action verbs
2. Include specific metrics where possible
3. Align with the job requirements
4. Follow the CAR format (Context, Action, Result)

Return only the 5 bullet points, one per line."""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            if response.status_code == 200:
                content = response.json()['content'][0]['text']
                return content.strip().split('\n')
            else:
                return []
        except Exception as e:
            print(f"Error generating content: {e}")
            return []


class JobAnalyzerCLI:
    """Command-line interface for job market analysis."""
    
    def __init__(self):
        self.firecrawl_key = os.environ.get('FIRECRAWL_API_KEY')
        self.claude_key = os.environ.get('CLAUDE_API_KEY')

        if not self.firecrawl_key:
            raise EnvironmentError(
                'FIRECRAWL_API_KEY is required. Set it in your environment or .env file.'
            )
        if not self.claude_key:
            raise EnvironmentError(
                'CLAUDE_API_KEY is required. Set it in your environment or .env file.'
            )

        self.scraper = FirecrawlJobScraper(self.firecrawl_key)
        self.claude = ClaudeAnalyzer(self.claude_key)
        
        # Standard analyzers
        self.analyzer = JobAnalyzer()
        self.optimizer = ResumeOptimizer()
        self.reporter = JobMarketReport()
        
    def scrape_jobs(self, source: str, role: str, num_jobs: int = 20) -> List[Dict]:
        """Scrape jobs from specified source using Firecrawl."""
        jobs = []
        
        if source == "meta":
            # Scrape Meta careers
            url = f"https://www.metacareers.com/jobs"
            print(f"🔍 Scraping Meta careers for {role}...")
            
            # First, search for the careers page
            search_results = self.scraper.search_web(f"Meta {role} careers jobs", num_results=10)
            
            # Extract job URLs
            job_urls = []
            for result in search_results:
                if 'metacareers.com' in result.get('url', '') and '/jobs/' in result.get('url', ''):
                    job_urls.append(result['url'])
            
            # Scrape each job with structured extraction
            schema = JobPostingExtractor.get_job_extraction_schema()
            for url in job_urls[:num_jobs]:
                print(f"  📄 Extracting: {url}")
                job_data = self.scraper.scrape_url(url, extract_schema=schema)
                if job_data and job_data.get('success'):
                    jobs.append(job_data.get('data', {}))
                    
        elif source == "linkedin":
            print(f"🔍 Searching LinkedIn for {role}...")
            # Use Firecrawl search to find LinkedIn job postings
            search_query = f"site:linkedin.com/jobs {role} {datetime.now().year}"
            results = self.scraper.search_web(search_query, num_results=num_jobs)
            
            for result in results:
                if result.get('url') and 'linkedin.com/jobs' in result['url']:
                    # Extract basic info from search results
                    jobs.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('content', ''),
                        'company': 'LinkedIn Job Posting'
                    })
                    
        elif source == "multi":
            companies = ["Meta", "Google", "Apple", "Amazon", "Microsoft", "Netflix", "Uber", "Airbnb"]
            
            for company in companies:
                print(f"🏢 Searching {company} for {role}...")
                query = f"{company} {role} careers jobs {datetime.now().year}"
                results = self.scraper.search_web(query, num_results=3)
                
                for result in results:
                    url = result.get('url', '')
                    if 'career' in url.lower() or 'job' in url.lower():
                        # Try to extract structured data
                        schema = JobPostingExtractor.get_job_extraction_schema()
                        job_data = self.scraper.scrape_url(url, extract_schema=schema)
                        
                        if job_data and job_data.get('success'):
                            job_info = job_data.get('data', {})
                            job_info['company'] = company
                            jobs.append(job_info)
                        else:
                            # Fallback to basic extraction
                            jobs.append({
                                'company': company,
                                'title': result.get('title', ''),
                                'url': url,
                                'description': result.get('content', '')
                            })
                            
        return jobs
    
    def analyze_with_claude(self, jobs: List[Dict], resume_text: Optional[str] = None) -> Dict:
        """Use Claude to provide intelligent analysis of jobs and resume fit."""
        analysis_results = {
            'job_insights': [],
            'resume_matches': [],
            'overall_recommendations': []
        }
        
        if resume_text:
            print("\n🤖 Using Claude AI for intelligent analysis...")
            
            # Analyze each job against the resume
            for job in jobs[:5]:  # Analyze top 5 jobs to manage API usage
                job_desc = job.get('description', '')
                if job_desc:
                    print(f"  📊 Analyzing fit for: {job.get('title', 'Unknown Title')}")
                    fit_analysis = self.claude.analyze_job_fit(job_desc, resume_text)
                    
                    if fit_analysis:
                        analysis_results['resume_matches'].append({
                            'job_title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'fit_analysis': fit_analysis
                        })
            
            # Generate tailored content based on common requirements
            all_requirements = []
            for job in jobs:
                if 'skills_required' in job:
                    all_requirements.extend(job['skills_required'])
                    
            if all_requirements:
                print("  ✍️  Generating tailored resume content...")
                tailored_bullets = self.claude.generate_tailored_content(
                    all_requirements[:10], 
                    resume_text[:500]  # First 500 chars as context
                )
                analysis_results['tailored_bullets'] = tailored_bullets
                
        return analysis_results
    
    def analyze_resume_file(self, resume_path: str) -> str:
        """Read and return resume content from file."""
        try:
            with open(resume_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Error: Resume file not found at {resume_path}")
            return ""
    
    def run_analysis(self, args):
        """Run the complete job analysis workflow."""
        print(f"\n🚀 Job Market Analyzer - {args.role}")
        print("=" * 60)
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"🔧 Using: Firecrawl + Claude AI")
        
        # Step 1: Scrape jobs
        print(f"\n📊 Scraping {args.source} for {args.role} positions...")
        jobs = self.scrape_jobs(args.source, args.role, args.num_jobs)
        print(f"✅ Found {len(jobs)} job postings")
        
        if not jobs:
            print("❌ No jobs found. Please check your search criteria.")
            return
        
        # Step 2: Analyze jobs with standard analyzer
        print("\n🔬 Analyzing job requirements...")
        job_analysis = self.analyzer.analyze_jobs(jobs)
        
        # Print quick insights
        print("\n📈 Market Insights:")
        for category, skills in job_analysis['skills_frequency'].items():
            if skills:
                top_skills = skills.most_common(3)
                if top_skills:
                    print(f"\n  {category.capitalize()} Skills:")
                    for skill, count in top_skills:
                        print(f"    • {skill}: {count} mentions")
        
        # Step 3: Claude AI Analysis if resume provided
        claude_analysis = {}
        if args.resume:
            print(f"\n📄 Loading resume: {args.resume}")
            resume_text = self.analyze_resume_file(args.resume)
            
            if resume_text:
                # Standard gap analysis
                resume_gaps = self.optimizer.analyze_resume_gaps(resume_text, job_analysis)
                
                # Claude AI analysis
                claude_analysis = self.analyze_with_claude(jobs, resume_text)
                
                # Display Claude insights
                if claude_analysis.get('resume_matches'):
                    print("\n🎯 AI-Powered Resume Analysis:")
                    for match in claude_analysis['resume_matches'][:3]:
                        print(f"\n  📍 {match['job_title']} at {match['company']}")
                        fit = match.get('fit_analysis', {})
                        if isinstance(fit, dict):
                            print(f"    Match: {fit.get('match_percentage', 'N/A')}%")
                            
                            if fit.get('key_strengths'):
                                print("    ✅ Strengths:")
                                for strength in fit['key_strengths'][:2]:
                                    print(f"      • {strength}")
                                    
                            if fit.get('critical_gaps'):
                                print("    ⚠️  Gaps:")
                                for gap in fit['critical_gaps'][:2]:
                                    print(f"      • {gap}")
                
                # Display tailored bullets
                if claude_analysis.get('tailored_bullets'):
                    print("\n✍️  AI-Generated Resume Bullets:")
                    for bullet in claude_analysis['tailored_bullets'][:5]:
                        if bullet.strip():
                            print(f"  • {bullet.strip()}")
        
        # Step 4: Generate comprehensive report
        if args.output:
            print(f"\n📝 Generating detailed report: {args.output}")
            
            # Create comprehensive report data
            report_data = {
                'analysis_date': datetime.now().isoformat(),
                'role_analyzed': args.role,
                'source': args.source,
                'jobs_analyzed': len(jobs),
                'job_analysis': job_analysis,
                'claude_analysis': claude_analysis,
                'jobs_sample': jobs[:10]  # Include first 10 jobs
            }
            
            if args.resume and 'resume_gaps' in locals():
                report_data['resume_gaps'] = resume_gaps
                
            # Save based on format
            if args.output.endswith('.json'):
                with open(args.output, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
            else:
                # Generate enhanced markdown report
                report = self._generate_enhanced_report(report_data)
                with open(args.output, 'w') as f:
                    f.write(report)
                    
            print(f"✅ Report saved to {args.output}")
        
        print("\n🎉 Analysis complete!")
        print("\n💡 Next Steps:")
        print("  1. Review the AI-generated insights")
        print("  2. Update your resume with suggested keywords")
        print("  3. Use the tailored bullets in your applications")
        print("  4. Target companies with the highest match scores")
    
    def _generate_enhanced_report(self, report_data: Dict) -> str:
        """Generate an enhanced markdown report with Claude insights."""
        report = []
        
        # Header
        report.append("# 🚀 Job Market Analysis Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Role:** {report_data.get('role_analyzed', 'N/A')}")
        report.append(f"**Jobs Analyzed:** {report_data.get('jobs_analyzed', 0)}")
        report.append(f"**Analysis Tools:** Firecrawl + Claude AI\n")
        
        # Executive Summary
        report.append("## 📊 Executive Summary")
        
        # Add Claude insights if available
        claude_analysis = report_data.get('claude_analysis', {})
        if claude_analysis.get('resume_matches'):
            report.append("\n### 🤖 AI Match Analysis")
            for match in claude_analysis['resume_matches'][:5]:
                fit = match.get('fit_analysis', {})
                if isinstance(fit, dict):
                    report.append(f"\n**{match['job_title']}** at {match['company']}")
                    report.append(f"- Match Score: {fit.get('match_percentage', 'N/A')}%")
                    
                    strengths = fit.get('key_strengths', [])
                    if strengths:
                        report.append("- Key Strengths: " + ", ".join(strengths[:3]))
                    
                    gaps = fit.get('critical_gaps', [])
                    if gaps:
                        report.append("- Critical Gaps: " + ", ".join(gaps[:3]))
        
        # Skills Analysis
        report.append("\n## 💼 Market Skills Analysis")
        job_analysis = report_data.get('job_analysis', {})
        for category, skills in job_analysis.get('skills_frequency', {}).items():
            if skills:
                report.append(f"\n### {category.capitalize()}")
                for skill, count in skills.most_common(10):
                    report.append(f"- {skill}: {count} mentions")
        
        # AI-Generated Content
        if claude_analysis.get('tailored_bullets'):
            report.append("\n## ✍️ AI-Generated Resume Bullets")
            report.append("*Use these tailored bullets in your resume:*\n")
            for bullet in claude_analysis['tailored_bullets']:
                if bullet.strip():
                    report.append(f"• {bullet.strip()}")
        
        # Job Listings Sample
        report.append("\n## 📋 Sample Job Listings")
        jobs = report_data.get('jobs_sample', [])
        for i, job in enumerate(jobs[:10], 1):
            report.append(f"\n### {i}. {job.get('title', 'Unknown Title')}")
            report.append(f"**Company:** {job.get('company', 'Unknown')}")
            report.append(f"**URL:** {job.get('url', 'N/A')}")
            
            skills = job.get('skills_required', [])
            if skills:
                report.append(f"**Key Skills:** {', '.join(skills[:5])}")
        
        return "\n".join(report)
    
    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n🚀 Job Market Analyzer - Interactive Mode")
        print("Powered by Firecrawl + Claude AI")
        print("=" * 60)
        
        # Get user inputs
        role = input("\n🎯 What role are you targeting? (e.g., Product Manager): ").strip()
        source = input("📍 Which source to scrape? (meta/linkedin/multi): ").strip().lower()
        
        resume_path = input("\n📄 Path to your resume (press Enter to skip): ").strip()
        
        num_jobs = input("🔢 How many jobs to analyze? (default: 20): ").strip()
        num_jobs = int(num_jobs) if num_jobs else 20
        
        output_format = input("\n📊 Output format? (markdown/json): ").strip().lower() or "markdown"
        output_file = f"job_analysis_{role.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.{output_format}"
        
        # Create args object
        class Args:
            pass
            
        args = Args()
        args.role = role
        args.source = source
        args.num_jobs = num_jobs
        args.resume = resume_path if resume_path else None
        args.output = output_file
        args.generate_bullets = True
        
        # Run analysis
        self.run_analysis(args)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🚀 Job Market Analyzer - AI-Powered Career Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 Examples:
  # Analyze Meta PM roles
  python job_analyzer_cli.py --role "Product Manager" --source meta

  # Analyze with resume comparison
  python job_analyzer_cli.py --role "Senior PM" --source multi --resume my_resume.txt

  # Full analysis with report
  python job_analyzer_cli.py --role "Product Manager" --source meta --resume resume.txt --output report.md

  # Interactive mode
  python job_analyzer_cli.py --interactive

💡 Features:
  • Real-time job scraping with Firecrawl
  • AI-powered analysis with Claude
  • Resume gap analysis
  • Tailored bullet generation
  • Comprehensive reports
        """
    )
    
    parser.add_argument('--role', type=str, default="Product Manager",
                       help='Job role to search for (default: Product Manager)')
    
    parser.add_argument('--source', type=str, choices=['meta', 'linkedin', 'multi'],
                       default='meta', help='Source to scrape jobs from')
    
    parser.add_argument('--num-jobs', type=int, default=20,
                       help='Number of jobs to analyze (default: 20)')
    
    parser.add_argument('--resume', type=str,
                       help='Path to your resume file for gap analysis')
    
    parser.add_argument('--output', type=str,
                       help='Output file for the report (markdown or json)')
    
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = JobAnalyzerCLI()
    
    print("\n🔧 Initializing Job Market Analyzer...")
    print("✅ Firecrawl API: Connected")
    print("✅ Claude AI: Connected")
    
    # Run in interactive mode or with args
    if args.interactive:
        cli.interactive_mode()
    else:
        cli.run_analysis(args)


if __name__ == "__main__":
    main()