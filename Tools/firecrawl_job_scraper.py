#!/usr/bin/env python3
"""
Firecrawl Job Scraper - Use Firecrawl API to scrape job postings
from company career pages and job boards.
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import requests


class FirecrawlJobScraper:
    """Scrape job postings using Firecrawl API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v0"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def scrape_url(self, url: str, extract_schema: Optional[Dict] = None) -> Dict:
        """Scrape a single URL using Firecrawl."""
        endpoint = f"{self.base_url}/scrape"
        
        payload = {
            "url": url,
            "pageOptions": {
                "onlyMainContent": True,
                "includeHtml": False
            }
        }
        
        if extract_schema:
            payload["extractorOptions"] = {
                "mode": "llm-extraction",
                "extractionSchema": extract_schema
            }
            
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error scraping {url}: {response.status_code}")
            return {}
    
    def crawl_site(self, url: str, max_pages: int = 20, 
                   include_pattern: Optional[str] = None) -> List[Dict]:
        """Crawl a website to find multiple job postings."""
        endpoint = f"{self.base_url}/crawl"
        
        payload = {
            "url": url,
            "crawlerOptions": {
                "maxPages": max_pages,
                "includes": [include_pattern] if include_pattern else None
            },
            "pageOptions": {
                "onlyMainContent": True
            }
        }
        
        # Start crawl
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error starting crawl: {response.status_code}")
            return []
            
        job_id = response.json().get("jobId")
        
        # Poll for results
        return self._poll_crawl_job(job_id)
    
    def _poll_crawl_job(self, job_id: str, timeout: int = 300) -> List[Dict]:
        """Poll crawl job status until complete."""
        endpoint = f"{self.base_url}/crawl/status/{job_id}"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(endpoint, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    return data.get("data", [])
                elif status == "failed":
                    print("Crawl job failed")
                    return []
                    
            time.sleep(2)  # Wait before polling again
            
        print("Crawl job timed out")
        return []
    
    def search_web(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search the web for job postings."""
        endpoint = f"{self.base_url}/search"
        
        payload = {
            "query": query,
            "pageOptions": {
                "fetchPageContent": True,
                "onlyMainContent": True
            },
            "searchOptions": {
                "limit": num_results
            }
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Error searching: {response.status_code}")
            return []


class JobPostingExtractor:
    """Extract structured job data from scraped content."""
    
    @staticmethod
    def get_job_extraction_schema() -> Dict:
        """Define schema for extracting job posting data."""
        return {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "description": "The title of the job position"
                },
                "company": {
                    "type": "string",
                    "description": "The company offering the position"
                },
                "location": {
                    "type": "string",
                    "description": "Job location (city, state, remote, etc.)"
                },
                "employment_type": {
                    "type": "string",
                    "description": "Full-time, part-time, contract, etc."
                },
                "experience_required": {
                    "type": "string",
                    "description": "Years of experience required"
                },
                "skills_required": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of required skills"
                },
                "nice_to_have_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of preferred but not required skills"
                },
                "responsibilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key job responsibilities"
                },
                "qualifications": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required qualifications"
                },
                "salary_range": {
                    "type": "string",
                    "description": "Salary range if mentioned"
                },
                "benefits": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Benefits offered"
                },
                "application_deadline": {
                    "type": "string",
                    "description": "Application deadline if mentioned"
                }
            }
        }
    
    @staticmethod
    def process_job_data(raw_data: List[Dict]) -> List[Dict]:
        """Process and clean extracted job data."""
        processed_jobs = []
        
        for item in raw_data:
            if 'llm_extraction' in item:
                job_data = item['llm_extraction']
                job_data['source_url'] = item.get('url', '')
                job_data['scraped_date'] = datetime.now().isoformat()
                processed_jobs.append(job_data)
                
        return processed_jobs


def scrape_meta_jobs(api_key: str) -> List[Dict]:
    """Scrape Product Manager jobs from Meta careers page."""
    scraper = FirecrawlJobScraper(api_key)
    extractor = JobPostingExtractor()
    
    # Meta careers search URL for Product Manager roles
    meta_careers_url = "https://www.metacareers.com/jobs?roles[0]=Product%20Manager"
    
    print("Crawling Meta careers page...")
    pages = scraper.crawl_site(
        meta_careers_url,
        max_pages=20,
        include_pattern="/jobs/\\d+"  # Pattern for individual job pages
    )
    
    jobs = []
    schema = extractor.get_job_extraction_schema()
    
    print(f"Found {len(pages)} job pages. Extracting details...")
    for page in pages:
        job_url = page.get('url', '')
        if '/jobs/' in job_url:
            print(f"Extracting: {job_url}")
            result = scraper.scrape_url(job_url, extract_schema=schema)
            if result:
                jobs.append(result)
                
    return extractor.process_job_data(jobs)


def scrape_tech_pm_jobs(api_key: str, companies: List[str]) -> List[Dict]:
    """Scrape PM jobs from multiple tech companies."""
    scraper = FirecrawlJobScraper(api_key)
    all_jobs = []
    
    for company in companies:
        query = f"{company} product manager jobs careers page"
        print(f"Searching for {company} PM jobs...")
        
        results = scraper.search_web(query, num_results=5)
        
        for result in results:
            url = result.get('url', '')
            if 'careers' in url or 'jobs' in url:
                print(f"Found careers page: {url}")
                # Crawl the careers page
                pages = scraper.crawl_site(url, max_pages=10)
                all_jobs.extend(pages)
                
    return all_jobs


def generate_job_market_report(jobs: List[Dict], output_file: str = "job_market_report.md"):
    """Generate a comprehensive job market report from scraped jobs."""
    report = []
    
    # Header
    report.append("# Job Market Analysis Report - Product Manager Roles")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Total Jobs Analyzed: {len(jobs)}\n")
    
    # Skills Analysis
    all_skills = []
    all_qualifications = []
    experience_levels = []
    
    for job in jobs:
        all_skills.extend(job.get('skills_required', []))
        all_skills.extend(job.get('nice_to_have_skills', []))
        all_qualifications.extend(job.get('qualifications', []))
        exp = job.get('experience_required', '')
        if exp:
            experience_levels.append(exp)
    
    # Count frequencies
    from collections import Counter
    skill_counts = Counter(all_skills)
    qual_counts = Counter(all_qualifications)
    
    report.append("## Top Required Skills")
    for skill, count in skill_counts.most_common(15):
        report.append(f"- {skill}: {count} jobs")
        
    report.append("\n## Common Qualifications")
    for qual, count in qual_counts.most_common(10):
        report.append(f"- {qual}: {count} jobs")
        
    report.append("\n## Experience Requirements")
    exp_counts = Counter(experience_levels)
    for exp, count in exp_counts.most_common():
        report.append(f"- {exp}: {count} jobs")
        
    # Job Details
    report.append("\n## Job Listings")
    for i, job in enumerate(jobs[:20], 1):  # Show first 20 jobs
        report.append(f"\n### {i}. {job.get('job_title', 'Unknown Title')}")
        report.append(f"**Company:** {job.get('company', 'Unknown')}")
        report.append(f"**Location:** {job.get('location', 'Unknown')}")
        report.append(f"**Experience:** {job.get('experience_required', 'Not specified')}")
        
        skills = job.get('skills_required', [])
        if skills:
            report.append(f"**Key Skills:** {', '.join(skills[:5])}")
            
        report.append(f"**Source:** {job.get('source_url', '')}")
        
    # Save report
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))
        
    print(f"\nReport saved to {output_file}")
    return '\n'.join(report)


def main():
    """Main execution function."""
    # Check for Firecrawl API key
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("Error: FIRECRAWL_API_KEY environment variable not set")
        print("Please set it with: export FIRECRAWL_API_KEY='your-api-key'")
        return
    
    print("Starting Firecrawl Job Market Analysis...")
    
    # Option 1: Scrape Meta jobs specifically
    print("\n1. Scraping Meta Product Manager jobs...")
    meta_jobs = scrape_meta_jobs(api_key)
    
    # Option 2: Search for PM jobs across multiple companies
    print("\n2. Searching for PM jobs at top tech companies...")
    companies = ["Google", "Apple", "Amazon", "Microsoft", "Netflix"]
    tech_jobs = scrape_tech_pm_jobs(api_key, companies)
    
    # Combine all jobs
    all_jobs = meta_jobs + tech_jobs
    
    # Generate report
    if all_jobs:
        generate_job_market_report(all_jobs)
    else:
        print("No jobs found. Please check your API key and internet connection.")


if __name__ == "__main__":
    main()