'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnalysisResult } from '@/types';
import { ResultsChart } from '@/components/ResultsChart/ResultsChart';
import { 
  ArrowLeft, 
  Target, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Download,
  Share2
} from 'lucide-react';

export default function Results() {
  const router = useRouter();
  const [results, setResults] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    const storedResults = sessionStorage.getItem('analysisResults');
    if (storedResults) {
      setResults(JSON.parse(storedResults));
    } else {
      router.push('/');
    }
  }, [router]);

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'APPLY_NOW': return 'text-green-600 bg-green-50';
      case 'APPLY_AFTER_IMPROVEMENTS': return 'text-amber-600 bg-amber-50';
      case 'BUILD_MORE_EXPERIENCE': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'APPLY_NOW': return CheckCircle;
      case 'APPLY_AFTER_IMPROVEMENTS': return TrendingUp;
      case 'BUILD_MORE_EXPERIENCE': return AlertTriangle;
      default: return Target;
    }
  };

  const handleDownloadReport = () => {
    const report = {
      ...results,
      generatedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `job-analysis-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Analysis</span>
          </button>
          
          <div className="flex space-x-2">
            <button
              onClick={handleDownloadReport}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8">
          {/* Summary Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Your Analysis Results</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Average Match</p>
                <p className="text-2xl font-bold text-gray-900">{results.summary.average_score}%</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-green-600 mb-1">Apply Now</p>
                <p className="text-2xl font-bold text-green-700">{results.summary.apply_now_count}</p>
              </div>
              <div className="bg-amber-50 p-4 rounded-lg">
                <p className="text-sm text-amber-600 mb-1">Need Improvements</p>
                <p className="text-2xl font-bold text-amber-700">{results.summary.apply_after_count}</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-600 mb-1">Build Experience</p>
                <p className="text-2xl font-bold text-red-700">{results.summary.build_exp_count}</p>
              </div>
            </div>

            {/* Chart */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Match Scores by Role</h2>
              <ResultsChart jobMatches={results.job_matches} />
            </div>
          </div>

          {/* Detailed Results */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Detailed Analysis</h2>
            
            {results.job_matches.map((match, index) => {
              const Icon = getRecommendationIcon(match.analysis.recommendation);
              
              return (
                <div key={index} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{match.job_title}</h3>
                      <p className="text-sm text-gray-600">{match.location}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">{match.analysis.match_percentage}%</p>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRecommendationColor(match.analysis.recommendation)}`}>
                        <Icon className="w-4 h-4 mr-1" />
                        {match.analysis.recommendation.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">✅ Strengths</h4>
                      <ul className="space-y-1">
                        {match.analysis.key_strengths.map((strength, i) => (
                          <li key={i} className="text-sm text-gray-600">• {strength}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">⚠️ Gaps</h4>
                      <ul className="space-y-1">
                        {match.analysis.critical_gaps.map((gap, i) => (
                          <li key={i} className="text-sm text-gray-600">• {gap}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">💡 Suggestions</h4>
                      <ul className="space-y-1">
                        {match.analysis.specific_suggestions.map((suggestion, i) => (
                          <li key={i} className="text-sm text-gray-600">• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </main>
  );
}