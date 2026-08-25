#!/usr/bin/env python3
"""
Job Market Analyzer - Scrape job postings and analyze requirements
to optimize your resume for specific roles.
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

class JobScraper:
    """Scrape job postings from various job boards and company career pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_meta_jobs(self, role: str = "product manager", num_jobs: int = 20) -> List[Dict]:
        """Scrape job postings from Meta careers page."""
        jobs = []
        
        # Meta careers API endpoint
        base_url = "https://www.metacareers.com/api/jobs"
        params = {
            'q': role,
            'location': 'United States',
            'limit': num_jobs
        }
        
        try:
            response = requests.get(base_url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                for job in data.get('jobs', []):
                    jobs.append({
                        'id': job.get('id'),
                        'title': job.get('title'),
                        'location': job.get('location'),
                        'description': job.get('description'),
                        'requirements': job.get('requirements'),
                        'posted_date': job.get('posted_date'),
                        'url': f"https://www.metacareers.com/jobs/{job.get('id')}"
                    })
        except Exception as e:
            print(f"Error scraping Meta jobs: {e}")
            
        return jobs
    
    def scrape_linkedin_jobs(self, role: str, location: str = "United States", num_jobs: int = 20) -> List[Dict]:
        """Scrape job postings from LinkedIn."""
        jobs = []
        
        # LinkedIn jobs search URL
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card-container')[:num_jobs]
                
                for card in job_cards:
                    job = {
                        'title': card.find('h3', class_='job-card-title').text.strip(),
                        'company': card.find('h4', class_='job-card-company').text.strip(),
                        'location': card.find('span', class_='job-card-location').text.strip(),
                        'url': card.find('a')['href'],
                        'description': self._get_job_description(card.find('a')['href'])
                    }
                    jobs.append(job)
        except Exception as e:
            print(f"Error scraping LinkedIn jobs: {e}")
            
        return jobs
    
    def _get_job_description(self, job_url: str) -> str:
        """Fetch full job description from job URL."""
        try:
            response = requests.get(job_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                description_div = soup.find('div', class_='job-description')
                return description_div.text if description_div else ""
        except:
            return ""


class JobAnalyzer:
    """Analyze job postings to extract key requirements and skills."""
    
    def __init__(self):
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
            
        self.skill_keywords = {
            'technical': ['python', 'sql', 'data', 'analytics', 'api', 'dashboard', 'metrics',
                         'a/b testing', 'experimentation', 'machine learning', 'ml', 'ai'],
            'product': ['roadmap', 'strategy', 'user research', 'product vision', 'prioritization',
                       'requirements', 'user stories', 'backlog', 'mvp', 'product lifecycle'],
            'leadership': ['leadership', 'team', 'mentor', 'cross-functional', 'stakeholder',
                          'influence', 'communication', 'collaboration', 'manage', 'lead'],
            'business': ['business strategy', 'roi', 'kpi', 'okr', 'metrics', 'growth',
                        'market analysis', 'competitive analysis', 'go-to-market', 'gtm'],
            'experience': ['years', 'experience', 'proven', 'track record', 'successful',
                          'shipped', 'launched', 'delivered', 'built', 'scaled']
        }
        
    def analyze_jobs(self, jobs: List[Dict]) -> Dict:
        """Analyze multiple job postings to extract common patterns."""
        analysis = {
            'total_jobs': len(jobs),
            'common_requirements': Counter(),
            'skills_frequency': defaultdict(Counter),
            'experience_requirements': [],
            'education_requirements': [],
            'certifications': [],
            'tools_mentioned': Counter(),
            'soft_skills': Counter(),
            'responsibilities': []
        }
        
        for job in jobs:
            description = job.get('description', '') + ' ' + job.get('requirements', '')
            
            # Extract requirements
            requirements = self._extract_requirements(description)
            analysis['common_requirements'].update(requirements)
            
            # Extract skills by category
            for category, keywords in self.skill_keywords.items():
                skills = self._extract_skills(description, keywords)
                analysis['skills_frequency'][category].update(skills)
            
            # Extract experience requirements
            exp_reqs = self._extract_experience(description)
            analysis['experience_requirements'].extend(exp_reqs)
            
            # Extract education requirements
            edu_reqs = self._extract_education(description)
            analysis['education_requirements'].extend(edu_reqs)
            
        return analysis
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract key requirements from job description."""
        requirements = []
        
        # Look for requirement patterns
        req_patterns = [
            r'required:?\s*(.*?)(?:\n|$)',
            r'requirements:?\s*(.*?)(?:\n|$)',
            r'must have:?\s*(.*?)(?:\n|$)',
            r'looking for:?\s*(.*?)(?:\n|$)'
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE | re.MULTILINE)
            requirements.extend(matches)
            
        return requirements
    
    def _extract_skills(self, text: str, keywords: List[str]) -> List[str]:
        """Extract specific skills mentioned in the text."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in keywords:
            if skill in text_lower:
                found_skills.append(skill)
                
        return found_skills
    
    def _extract_experience(self, text: str) -> List[str]:
        """Extract experience requirements."""
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?\s*(?:of\s*)?experience'
        ]
        
        experiences = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            experiences.extend([str(match) for match in matches])
            
        return experiences
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements."""
        edu_keywords = ['bachelor', 'master', 'phd', 'mba', 'degree', 'bs', 'ms', 'ba', 'ma']
        text_lower = text.lower()
        
        education = []
        for keyword in edu_keywords:
            if keyword in text_lower:
                # Extract context around the keyword
                pattern = rf'\b{keyword}\b.{{0,50}}'
                matches = re.findall(pattern, text_lower)
                education.extend(matches)
                
        return education


class ResumeOptimizer:
    """Compare resume against job requirements and suggest improvements."""
    
    def __init__(self):
        self.resume_sections = ['experience', 'skills', 'education', 'projects', 'achievements']
        
    def analyze_resume_gaps(self, resume_text: str, job_analysis: Dict) -> Dict:
        """Identify gaps between resume and job requirements."""
        gaps = {
            'missing_skills': defaultdict(list),
            'keyword_gaps': [],
            'experience_gaps': [],
            'improvement_suggestions': []
        }
        
        resume_lower = resume_text.lower()
        
        # Check for missing skills
        for category, skills in job_analysis['skills_frequency'].items():
            for skill, count in skills.most_common(10):
                if skill not in resume_lower and count > 2:
                    gaps['missing_skills'][category].append({
                        'skill': skill,
                        'frequency': count,
                        'importance': 'high' if count > 5 else 'medium'
                    })
        
        # Check for missing keywords
        top_requirements = job_analysis['common_requirements'].most_common(20)
        for req, count in top_requirements:
            if req not in resume_lower:
                gaps['keyword_gaps'].append({
                    'keyword': req,
                    'frequency': count
                })
        
        # Generate improvement suggestions
        gaps['improvement_suggestions'] = self._generate_suggestions(gaps)
        
        return gaps
    
    def _generate_suggestions(self, gaps: Dict) -> List[str]:
        """Generate specific improvement suggestions based on gaps."""
        suggestions = []
        
        # Skill suggestions
        for category, skills in gaps['missing_skills'].items():
            if skills:
                high_priority = [s['skill'] for s in skills if s['importance'] == 'high']
                if high_priority:
                    suggestions.append(
                        f"Add {category} skills to your resume: {', '.join(high_priority[:3])}"
                    )
        
        # Keyword suggestions
        if gaps['keyword_gaps']:
            top_keywords = [k['keyword'] for k in gaps['keyword_gaps'][:5]]
            suggestions.append(
                f"Include these keywords in your experience section: {', '.join(top_keywords)}"
            )
        
        return suggestions
    
    def generate_tailored_bullets(self, job_analysis: Dict) -> List[str]:
        """Generate resume bullet points tailored to job requirements."""
        bullets = []
        
        # Extract top skills and requirements
        top_skills = []
        for category, skills in job_analysis['skills_frequency'].items():
            top_skills.extend([skill for skill, _ in skills.most_common(3)])
        
        # Generate bullet templates
        templates = [
            "Led cross-functional team to deliver {project} using {skill}, resulting in {metric}",
            "Developed and implemented {solution} leveraging {skill} to improve {outcome}",
            "Analyzed {data/process} using {skill} to identify {insight} and drive {result}",
            "Collaborated with {stakeholders} to define {deliverable} requirements using {methodology}",
            "Managed {scope} project from conception to launch, utilizing {skill} to achieve {goal}"
        ]
        
        # Create specific bullets using top skills
        for template in templates[:3]:
            if top_skills:
                bullet = template.replace('{skill}', top_skills[0])
                bullets.append(bullet)
                top_skills = top_skills[1:]  # Rotate skills
                
        return bullets


class JobMarketReport:
    """Generate comprehensive job market analysis reports."""
    
    def __init__(self):
        self.report_sections = [
            'executive_summary',
            'market_overview',
            'skill_analysis',
            'requirement_trends',
            'resume_gaps',
            'recommendations'
        ]
        
    def generate_report(self, job_analysis: Dict, resume_gaps: Dict, 
                       output_format: str = 'markdown') -> str:
        """Generate a comprehensive job market analysis report."""
        
        if output_format == 'markdown':
            return self._generate_markdown_report(job_analysis, resume_gaps)
        elif output_format == 'json':
            return json.dumps({
                'job_analysis': job_analysis,
                'resume_gaps': resume_gaps,
                'generated_date': datetime.now().isoformat()
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _generate_markdown_report(self, job_analysis: Dict, resume_gaps: Dict) -> str:
        """Generate a markdown formatted report."""
        report = []
        
        # Header
        report.append("# Job Market Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append(f"- Analyzed {job_analysis['total_jobs']} job postings")
        report.append(f"- Identified {len(resume_gaps['missing_skills'])} skill gap categories")
        report.append(f"- Found {len(resume_gaps['keyword_gaps'])} missing keywords")
        report.append("")
        
        # Top Skills by Category
        report.append("## Top Skills by Category")
        for category, skills in job_analysis['skills_frequency'].items():
            if skills:
                report.append(f"\n### {category.capitalize()}")
                for skill, count in skills.most_common(5):
                    report.append(f"- {skill}: {count} mentions")
        report.append("")
        
        # Resume Optimization Suggestions
        report.append("## Resume Optimization Suggestions")
        for i, suggestion in enumerate(resume_gaps['improvement_suggestions'], 1):
            report.append(f"{i}. {suggestion}")
        report.append("")
        
        # Missing Skills Detail
        report.append("## Detailed Skill Gaps")
        for category, skills in resume_gaps['missing_skills'].items():
            if skills:
                report.append(f"\n### {category.capitalize()} Skills to Add:")
                for skill_info in skills:
                    priority = "🔴" if skill_info['importance'] == 'high' else "🟡"
                    report.append(f"- {priority} {skill_info['skill']} (mentioned {skill_info['frequency']} times)")
        
        return "\n".join(report)


# Main execution function
def main():
    """Run the complete job market analysis workflow."""
    print("Starting Job Market Analysis...")
    
    # Initialize components
    scraper = JobScraper()
    analyzer = JobAnalyzer()
    optimizer = ResumeOptimizer()
    reporter = JobMarketReport()
    
    # Scrape jobs (using mock data for now)
    print("Scraping job postings...")
    # In production, you would use actual scraping methods
    jobs = scraper.scrape_meta_jobs("product manager", 20)
    
    if not jobs:
        print("No jobs found. Using sample data for demonstration...")
        # Sample job data for testing
        jobs = [
            {
                'title': 'Senior Product Manager',
                'company': 'Meta',
                'description': '''
                We are looking for a Senior Product Manager with 5+ years of experience
                in consumer products. Must have strong analytical skills, SQL proficiency,
                and experience with A/B testing. Leadership experience required.
                Bachelor's degree in Computer Science or related field preferred.
                Experience with data analytics, user research, and cross-functional collaboration.
                '''
            }
        ]
    
    # Analyze jobs
    print("Analyzing job requirements...")
    job_analysis = analyzer.analyze_jobs(jobs)
    
    # Load resume (you would provide your actual resume text)
    resume_text = """
    Product Manager with 3 years of experience in B2B SaaS.
    Skills: Product strategy, roadmap planning, agile methodology.
    Education: Bachelor's in Business Administration.
    """
    
    # Analyze resume gaps
    print("Comparing resume against job requirements...")
    resume_gaps = optimizer.analyze_resume_gaps(resume_text, job_analysis)
    
    # Generate tailored bullets
    tailored_bullets = optimizer.generate_tailored_bullets(job_analysis)
    
    # Generate report
    print("Generating analysis report...")
    report = reporter.generate_report(job_analysis, resume_gaps)
    
    # Save report
    with open('job_market_analysis_report.md', 'w') as f:
        f.write(report)
        
    print("\nAnalysis complete! Report saved to job_market_analysis_report.md")
    
    # Print sample tailored bullets
    print("\nSample Tailored Resume Bullets:")
    for bullet in tailored_bullets[:3]:
        print(f"• {bullet}")


if __name__ == "__main__":
    main()