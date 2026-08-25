'use client';

import React, { useState } from 'react';
import { FileUpload } from '@/components/FileUpload/FileUpload';
import { CompanySelector } from '@/components/CompanySelector/CompanySelector';
import { Sparkles, AlertCircle } from 'lucide-react';
import { Company } from '@/types';
import { useRouter } from 'next/navigation';

const COMPANIES: Record<string, Company> = {
  meta: {
    id: 'meta',
    name: 'Meta',
    locations: ['Seattle, WA', 'Austin, TX', 'Menlo Park, CA', 'New York, NY'],
    roles: ['Product Manager', 'Technical Product Manager']
  },
  apple: {
    id: 'apple',
    name: 'Apple',
    locations: ['Cupertino, CA', 'Austin, TX', 'Seattle, WA'],
    roles: ['Product Manager', 'Technical Product Manager']
  },
  google: {
    id: 'google',
    name: 'Google',
    locations: ['Mountain View, CA', 'Seattle, WA', 'Austin, TX', 'New York, NY'],
    roles: ['Product Manager', 'Technical Program Manager']
  }
};

export default function Home() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedCompany, setSelectedCompany] = useState('meta');
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');

  const handleLocationToggle = (location: string) => {
    setSelectedLocations(prev => 
      prev.includes(location)
        ? prev.filter(l => l !== location)
        : [...prev, location]
    );
  };

  const handleAnalyze = async () => {
    if (!selectedFile || selectedLocations.length === 0) {
      setError('Please upload a resume and select at least one location');
      return;
    }

    setIsAnalyzing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('resume', selectedFile);
      formData.append('company', selectedCompany);
      selectedLocations.forEach(loc => formData.append('locations', loc));

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: apiKey ? { 'x-claude-api-key': apiKey } : {},
        body: formData
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const results = await response.json();
      
      // Store results and navigate
      sessionStorage.setItem('analysisResults', JSON.stringify(results));
      router.push('/results');
    } catch (err) {
      setError('Failed to analyze resume. Please try again.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Job Market Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered resume analysis for top tech companies
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 space-y-8">
          {/* API Key Input */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Claude API Key (Optional)
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-ant-api..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Add your Claude API key for better analysis (demo mode without key)
            </p>
          </div>

          {/* File Upload */}
          <div>
            <h2 className="text-xl font-semibold mb-4">1. Upload Your Resume</h2>
            <FileUpload
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile || undefined}
              onClear={() => setSelectedFile(null)}
            />
          </div>

          {/* Company Selection */}
          <div>
            <h2 className="text-xl font-semibold mb-4">2. Select Company & Locations</h2>
            <CompanySelector
              companies={COMPANIES}
              selectedCompany={selectedCompany}
              selectedLocations={selectedLocations}
              onCompanyChange={setSelectedCompany}
              onLocationToggle={handleLocationToggle}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center p-4 bg-red-50 rounded-lg text-red-700">
              <AlertCircle className="w-5 h-5 mr-2" />
              {error}
            </div>
          )}

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || selectedLocations.length === 0 || isAnalyzing}
            className="w-full py-4 px-6 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Analyze My Fit</span>
              </>
            )}
          </button>
        </div>

        <footer className="text-center mt-8 text-sm text-gray-500">
          Built with Next.js, TypeScript, and Claude AI
        </footer>
      </div>
    </main>
  );
}