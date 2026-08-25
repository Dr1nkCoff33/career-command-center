#!/usr/bin/env python3
"""
Semantic Matcher using BERTopic for improved resume-job matching.
This module uses transformer embeddings and topic modeling to better understand
the semantic similarity between resumes and job descriptions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class SemanticMatcher:
    """Use BERTopic and sentence embeddings for semantic matching between resumes and jobs."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic matcher with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.sentence_model = SentenceTransformer(model_name)
        self.topic_model = None
        
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better matching."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Keep important punctuation but remove excessive special characters
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)]', ' ', text)
        
        return text
    
    def extract_key_sections(self, resume_text: str) -> Dict[str, str]:
        """Extract key sections from resume for targeted matching."""
        sections = {
            'experience': '',
            'education': '',
            'skills': '',
            'full_text': resume_text
        }
        
        # Simple section extraction based on common headers
        lines = resume_text.split('\n')
        current_section = 'full_text'
        
        section_keywords = {
            'experience': ['experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'academic', 'degrees', 'certifications'],
            'skills': ['skills', 'competencies', 'expertise', 'technical skills']
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    break
            
            # Add content to current section
            if current_section in sections and current_section != 'full_text':
                sections[current_section] += line + '\n'
        
        return sections
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, str]:
        """Extract key requirements from job description."""
        requirements = {
            'responsibilities': '',
            'qualifications': '',
            'skills_required': '',
            'full_text': job_description
        }
        
        lines = job_description.split('\n')
        current_section = 'full_text'
        
        section_keywords = {
            'responsibilities': ['responsibilities', 'duties', 'key duties', 'what you will do'],
            'qualifications': ['qualifications', 'requirements', 'what we need', 'must have'],
            'skills_required': ['skills', 'competencies', 'technical requirements']
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    break
            
            if current_section in requirements and current_section != 'full_text':
                requirements[current_section] += line + '\n'
        
        return requirements
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using sentence embeddings."""
        # Preprocess texts
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        
        # Generate embeddings
        embeddings = self.sentence_model.encode([text1, text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(similarity)
    
    def analyze_topic_alignment(self, resume_text: str, job_description: str) -> Dict[str, any]:
        """Analyze topic alignment between resume and job using BERTopic."""
        # Combine texts for topic modeling
        documents = [
            self.preprocess_text(resume_text),
            self.preprocess_text(job_description)
        ]
        
        # Add more context by splitting into paragraphs
        resume_paragraphs = [p.strip() for p in resume_text.split('\n\n') if p.strip()]
        job_paragraphs = [p.strip() for p in job_description.split('\n\n') if p.strip()]
        
        documents.extend([self.preprocess_text(p) for p in resume_paragraphs[:10]])
        documents.extend([self.preprocess_text(p) for p in job_paragraphs[:10]])
        
        # Create topic model with custom settings for small corpus
        vectorizer_model = CountVectorizer(
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1
        )
        
        topic_model = BERTopic(
            embedding_model=self.sentence_model,
            vectorizer_model=vectorizer_model,
            nr_topics="auto",
            min_topic_size=2
        )
        
        # Fit the model
        topics, probs = topic_model.fit_transform(documents)
        
        # Get topic info
        topic_info = topic_model.get_topic_info()
        
        # Extract top terms from topics
        resume_topics = set()
        job_topics = set()
        
        # First document is resume, second is job description
        if topics[0] != -1:
            resume_topic_terms = topic_model.get_topic(topics[0])
            resume_topics.update([term[0] for term in resume_topic_terms[:10]])
        
        if topics[1] != -1:
            job_topic_terms = topic_model.get_topic(topics[1])
            job_topics.update([term[0] for term in job_topic_terms[:10]])
        
        # Calculate topic overlap
        common_topics = resume_topics.intersection(job_topics)
        topic_similarity = len(common_topics) / max(len(resume_topics), len(job_topics), 1)
        
        return {
            'resume_topics': list(resume_topics),
            'job_topics': list(job_topics),
            'common_topics': list(common_topics),
            'topic_similarity': topic_similarity,
            'num_topics_found': len(topic_info)
        }
    
    def calculate_comprehensive_match(self, resume_text: str, job_description: str) -> Dict[str, any]:
        """
        Calculate comprehensive match score using multiple semantic techniques.
        
        Returns:
            Dictionary containing match scores and analysis details
        """
        # Extract sections
        resume_sections = self.extract_key_sections(resume_text)
        job_requirements = self.extract_job_requirements(job_description)
        
        # Calculate overall similarity
        overall_similarity = self.calculate_semantic_similarity(
            resume_sections['full_text'],
            job_requirements['full_text']
        )
        
        # Calculate section-specific similarities
        section_scores = {}
        
        # Experience vs Responsibilities
        if resume_sections['experience'] and job_requirements['responsibilities']:
            section_scores['experience_match'] = self.calculate_semantic_similarity(
                resume_sections['experience'],
                job_requirements['responsibilities']
            )
        
        # Education & Skills vs Qualifications
        if resume_sections['education'] or resume_sections['skills']:
            combined_resume = resume_sections['education'] + '\n' + resume_sections['skills']
            if job_requirements['qualifications']:
                section_scores['qualification_match'] = self.calculate_semantic_similarity(
                    combined_resume,
                    job_requirements['qualifications']
                )
        
        # Skills specific match
        if resume_sections['skills'] and job_requirements['skills_required']:
            section_scores['skills_match'] = self.calculate_semantic_similarity(
                resume_sections['skills'],
                job_requirements['skills_required']
            )
        
        # Topic analysis
        topic_analysis = self.analyze_topic_alignment(resume_text, job_description)
        
        # Calculate weighted final score
        weights = {
            'overall': 0.3,
            'experience': 0.25,
            'qualifications': 0.2,
            'skills': 0.15,
            'topics': 0.1
        }
        
        weighted_score = (
            weights['overall'] * overall_similarity +
            weights['experience'] * section_scores.get('experience_match', overall_similarity) +
            weights['qualifications'] * section_scores.get('qualification_match', overall_similarity) +
            weights['skills'] * section_scores.get('skills_match', overall_similarity) +
            weights['topics'] * topic_analysis['topic_similarity']
        )
        
        # Convert to percentage
        match_percentage = round(weighted_score * 100, 1)
        
        return {
            'match_percentage': match_percentage,
            'overall_similarity': round(overall_similarity * 100, 1),
            'section_scores': {k: round(v * 100, 1) for k, v in section_scores.items()},
            'topic_analysis': topic_analysis,
            'semantic_insights': self._generate_insights(
                match_percentage,
                section_scores,
                topic_analysis
            )
        }
    
    def _generate_insights(self, match_percentage: float, section_scores: Dict, 
                          topic_analysis: Dict) -> List[str]:
        """Generate insights based on semantic analysis."""
        insights = []
        
        # Overall match insights
        if match_percentage >= 80:
            insights.append("Excellent semantic alignment between resume and job description")
        elif match_percentage >= 65:
            insights.append("Good semantic alignment with some areas for improvement")
        else:
            insights.append("Limited semantic alignment - significant gaps exist")
        
        # Section-specific insights
        if 'experience_match' in section_scores:
            if section_scores['experience_match'] < 50:
                insights.append("Experience section shows low alignment with job responsibilities")
            elif section_scores['experience_match'] > 75:
                insights.append("Strong experience alignment with job requirements")
        
        if 'skills_match' in section_scores:
            if section_scores['skills_match'] < 50:
                insights.append("Skills section needs better alignment with required competencies")
        
        # Topic insights
        if topic_analysis['common_topics']:
            insights.append(f"Key aligned topics: {', '.join(topic_analysis['common_topics'][:5])}")
        
        missing_topics = set(topic_analysis['job_topics']) - set(topic_analysis['resume_topics'])
        if missing_topics:
            insights.append(f"Consider incorporating: {', '.join(list(missing_topics)[:5])}")
        
        return insights
    
    def get_keyword_recommendations(self, resume_text: str, job_description: str) -> List[str]:
        """Generate keyword recommendations based on semantic gap analysis."""
        # Extract topics and terms from job that are missing in resume
        topic_analysis = self.analyze_topic_alignment(resume_text, job_description)
        
        missing_topics = set(topic_analysis['job_topics']) - set(topic_analysis['resume_topics'])
        
        # Use sentence transformer to find semantically similar terms
        recommendations = []
        
        # Add missing topics
        recommendations.extend(list(missing_topics)[:10])
        
        # Extract important phrases from job description
        job_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        # Common important phrases in job descriptions
        important_patterns = [
            r'\b(?:experience with|knowledge of|proficiency in|skilled in|expertise in)\s+([^.,\n]+)',
            r'\b(?:ability to|capable of|responsible for)\s+([^.,\n]+)',
            r'\b(?:required:|requirements:|must have:)\s*([^.\n]+)'
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, job_lower)
            for match in matches:
                # Check if this phrase is not in resume
                if match.strip() and match.strip() not in resume_lower:
                    recommendations.append(match.strip())
        
        # Remove duplicates and limit recommendations
        recommendations = list(dict.fromkeys(recommendations))[:15]
        
        return recommendations


def enhance_claude_analysis_with_semantics(
    claude_analysis: Dict,
    semantic_analysis: Dict
) -> Dict:
    """
    Enhance Claude's analysis with semantic matching insights.
    
    Args:
        claude_analysis: Original analysis from Claude
        semantic_analysis: Analysis from SemanticMatcher
        
    Returns:
        Enhanced analysis dictionary
    """
    # Update match percentage with weighted average
    claude_match = claude_analysis.get('match_percentage', 0)
    semantic_match = semantic_analysis['match_percentage']
    
    # Weight semantic analysis higher for technical matching
    enhanced_match = round(0.4 * claude_match + 0.6 * semantic_match, 1)
    
    enhanced_analysis = claude_analysis.copy()
    enhanced_analysis['match_percentage'] = enhanced_match
    enhanced_analysis['semantic_analysis'] = semantic_analysis
    
    # Add semantic insights to suggestions
    if 'specific_suggestions' in enhanced_analysis:
        enhanced_analysis['specific_suggestions'].extend(
            semantic_analysis['semantic_insights']
        )
    
    # Add keyword recommendations
    if 'missing_keywords' in enhanced_analysis and 'keyword_recommendations' in semantic_analysis:
        combined_keywords = list(set(
            enhanced_analysis['missing_keywords'] + 
            semantic_analysis.get('keyword_recommendations', [])
        ))
        enhanced_analysis['missing_keywords'] = combined_keywords[:20]
    
    return enhanced_analysis


# Example usage
if __name__ == "__main__":
    # Test with sample data
    matcher = SemanticMatcher()
    
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - 5 years developing web applications with Python and JavaScript
    - Led team of 4 engineers on cloud migration project
    - Implemented CI/CD pipelines using Jenkins and Docker
    
    Education:
    - BS Computer Science, University XYZ
    
    Skills:
    - Python, JavaScript, React, Node.js
    - AWS, Docker, Kubernetes
    - Agile, Scrum, Git
    """
    
    sample_job = """
    Senior Software Engineer
    
    Responsibilities:
    - Design and develop scalable web applications
    - Lead technical initiatives and mentor junior developers
    - Implement cloud-native solutions using AWS
    
    Requirements:
    - 5+ years software development experience
    - Strong experience with Python and modern JavaScript frameworks
    - Experience with containerization and orchestration tools
    - Knowledge of CI/CD best practices
    """
    
    result = matcher.calculate_comprehensive_match(sample_resume, sample_job)
    print(f"Match Score: {result['match_percentage']}%")
    print(f"Insights: {result['semantic_insights']}")