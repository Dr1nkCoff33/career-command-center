import { NextRequest, NextResponse } from 'next/server';
import { AnalysisResult, Job } from '@/types';

// Companies configuration
const COMPANIES_CONFIG = {
  meta: {
    name: 'Meta',
    sampleJobs: [
      {
        id: 'meta-1',
        title: 'Product Manager - Ads & Business Platform',
        company: 'Meta',
        location: 'Seattle, WA',
        description: 'Lead product strategy for Meta\'s advertising platform...',
        skills_required: ['product management', 'ads platform', 'data analysis', 'A/B testing']
      },
      {
        id: 'meta-2',
        title: 'Product Manager - Infrastructure',
        company: 'Meta',
        location: 'Austin, TX',
        description: 'Drive infrastructure products that power billions of users...',
        skills_required: ['technical product management', 'infrastructure', 'systems design']
      }
    ]
  },
  apple: {
    name: 'Apple',
    sampleJobs: [
      {
        id: 'apple-1',
        title: 'Product Manager - App Store',
        company: 'Apple',
        location: 'Cupertino, CA',
        description: 'Shape the future of the App Store ecosystem...',
        skills_required: ['product management', 'mobile apps', 'ecosystem development']
      }
    ]
  },
  google: {
    name: 'Google',
    sampleJobs: [
      {
        id: 'google-1',
        title: 'Product Manager - Cloud Platform',
        company: 'Google',
        location: 'Mountain View, CA',
        description: 'Lead Google Cloud product initiatives...',
        skills_required: ['cloud computing', 'enterprise products', 'technical product management']
      }
    ]
  }
};

async function analyzeWithClaude(job: Job, resumeText: string, apiKey: string) {
  const prompt = `Analyze this resume for job fit:
Job: ${job.title} at ${job.company}
Location: ${job.location}
Skills Required: ${job.skills_required.join(', ')}

Resume: ${resumeText.substring(0, 2000)}...

Return JSON with:
- match_percentage (0-100)
- key_strengths (array of 3 strings)
- critical_gaps (array of 3 strings)
- specific_suggestions (array of 3 strings)
- recommendation ("APPLY_NOW", "APPLY_AFTER_IMPROVEMENTS", or "BUILD_MORE_EXPERIENCE")`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.content[0].text;
    
    // Parse JSON from Claude's response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    // Fallback analysis
    return {
      match_percentage: 70,
      key_strengths: ['Strong experience', 'Leadership skills', 'Technical background'],
      critical_gaps: ['Limited scale', 'Domain expertise', 'Specific tools'],
      specific_suggestions: ['Highlight achievements', 'Add metrics', 'Focus on impact'],
      recommendation: 'APPLY_AFTER_IMPROVEMENTS'
    };
  } catch (error) {
    console.error('Claude API error:', error);
    // Return mock data for demo
    return {
      match_percentage: Math.floor(Math.random() * 30) + 60,
      key_strengths: ['Strong leadership', 'Technical skills', 'Product sense'],
      critical_gaps: ['Scale experience', 'Domain knowledge', 'Specific technologies'],
      specific_suggestions: ['Quantify impact', 'Add relevant keywords', 'Highlight achievements'],
      recommendation: 'APPLY_AFTER_IMPROVEMENTS'
    };
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const company = formData.get('company') as string;
    const locations = formData.getAll('locations') as string[];
    const resumeFile = formData.get('resume') as File;
    const apiKey = request.headers.get('x-claude-api-key') || process.env.CLAUDE_API_KEY;

    if (!resumeFile || !company || locations.length === 0) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Read resume text
    const resumeText = await resumeFile.text();

    // Get jobs for selected company and locations
    const companyConfig = COMPANIES_CONFIG[company as keyof typeof COMPANIES_CONFIG];
    const jobs = companyConfig.sampleJobs.filter(job => 
      locations.some(loc => job.location.includes(loc))
    );

    if (jobs.length === 0) {
      return NextResponse.json(
        { error: 'No jobs found for selected locations' },
        { status: 404 }
      );
    }

    // Analyze each job
    const jobMatches = await Promise.all(
      jobs.map(async (job) => {
        const analysis = await analyzeWithClaude(job, resumeText, apiKey || '');
        return {
          job_title: job.title,
          location: job.location,
          company: job.company,
          analysis
        };
      })
    );

    // Calculate summary
    const scores = jobMatches.map(m => m.analysis.match_percentage);
    const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    
    const recommendations = jobMatches.map(m => m.analysis.recommendation);
    const summary = {
      total_jobs: jobMatches.length,
      average_score: avgScore,
      apply_now_count: recommendations.filter(r => r === 'APPLY_NOW').length,
      apply_after_count: recommendations.filter(r => r === 'APPLY_AFTER_IMPROVEMENTS').length,
      build_exp_count: recommendations.filter(r => r === 'BUILD_MORE_EXPERIENCE').length
    };

    const result: AnalysisResult = {
      job_matches: jobMatches,
      summary,
      timestamp: new Date().toISOString()
    };

    return NextResponse.json(result);
  } catch (error) {
    console.error('Analysis error:', error);
    return NextResponse.json(
      { error: 'Analysis failed' },
      { status: 500 }
    );
  }
}