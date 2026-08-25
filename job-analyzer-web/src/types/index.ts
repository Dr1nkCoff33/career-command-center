export interface Company {
  id: string;
  name: string;
  locations: string[];
  roles: string[];
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  url?: string;
  skills_required: string[];
}

export interface ResumeData {
  text: string;
  fileName: string;
  uploadedAt: Date;
}

export interface JobAnalysis {
  match_percentage: number;
  key_strengths: string[];
  critical_gaps: string[];
  specific_suggestions: string[];
  recommendation: 'APPLY_NOW' | 'APPLY_AFTER_IMPROVEMENTS' | 'BUILD_MORE_EXPERIENCE';
}

export interface JobMatch {
  job_title: string;
  location: string;
  company: string;
  analysis: JobAnalysis;
}

export interface AnalysisResult {
  job_matches: JobMatch[];
  summary: {
    total_jobs: number;
    average_score: number;
    apply_now_count: number;
    apply_after_count: number;
    build_exp_count: number;
  };
  timestamp: string;
}