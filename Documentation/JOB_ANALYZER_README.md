# 🚀 Job Market Analyzer

An AI-powered tool that combines Firecrawl web scraping with Claude AI analysis to help you optimize your job search and tailor your resume for specific roles.

## ✨ Features

- **Real-time Job Scraping**: Scrape job postings from Meta, LinkedIn, and other tech companies
- **AI-Powered Analysis**: Use Claude to analyze job requirements and match them to your resume
- **Gap Analysis**: Identify missing skills and keywords in your resume
- **Tailored Content**: Generate AI-crafted resume bullets specific to job requirements
- **Comprehensive Reports**: Get detailed markdown or JSON reports with actionable insights

## 🔧 Setup

1. **Run the setup script**:
   ```bash
   chmod +x setup_job_analyzer.sh
   ./setup_job_analyzer.sh
   ```

2. **Or manually install dependencies**:
   ```bash
   pip install requests beautifulsoup4 nltk pandas
   ```

## 🎯 Usage Examples

### 1. Basic Job Analysis
```bash
# Analyze Product Manager roles at Meta
python job_analyzer_cli.py --role "Product Manager" --source meta

# Search across multiple companies
python job_analyzer_cli.py --role "Senior PM" --source multi
```

### 2. Resume Comparison
```bash
# Compare your resume against job requirements
python job_analyzer_cli.py \
    --role "Product Manager" \
    --source meta \
    --resume my_resume.txt \
    --output analysis_report.md
```

### 3. Interactive Mode
```bash
# Let the tool guide you through the process
python job_analyzer_cli.py --interactive
```

## 📊 What You'll Get

### 1. Market Insights
- Most requested skills by category (technical, product, leadership)
- Common requirements across companies
- Experience level expectations

### 2. Resume Analysis
- Match percentage for each job
- Missing keywords and skills
- Specific improvement suggestions

### 3. AI-Generated Content
- Tailored resume bullets that align with job requirements
- Keywords to incorporate
- Action verbs and metrics to include

## 🛠️ Advanced Options

```bash
# Analyze more jobs (default is 20)
python job_analyzer_cli.py --role "PM" --num-jobs 50

# Get JSON output for further processing
python job_analyzer_cli.py --role "PM" --output results.json

# Analyze LinkedIn jobs
python job_analyzer_cli.py --role "Product Manager" --source linkedin
```

## 📝 Example Output

```
🚀 Job Market Analyzer - Product Manager
============================================================
📅 Analysis Date: 2025-01-05 10:30
🔧 Using: Firecrawl + Claude AI

📊 Scraping meta for Product Manager positions...
✅ Found 25 job postings

📈 Market Insights:

  Technical Skills:
    • SQL: 18 mentions
    • Data Analytics: 15 mentions
    • A/B Testing: 12 mentions

  Product Skills:
    • Roadmap Planning: 20 mentions
    • User Research: 17 mentions
    • Prioritization: 14 mentions

🎯 AI-Powered Resume Analysis:

  📍 Senior Product Manager - AI/ML at Meta
    Match: 78%
    ✅ Strengths:
      • Strong product strategy experience
      • Cross-functional collaboration skills
    ⚠️ Gaps:
      • Limited ML/AI product experience
      • No mention of A/B testing

✍️ AI-Generated Resume Bullets:
  • Led cross-functional team of 12 to deliver ML-powered recommendation system, increasing user engagement by 35%
  • Designed and executed A/B testing framework for product features, analyzing results with SQL to drive data-driven decisions
  • Partnered with data science team to define success metrics and KPIs for AI features, resulting in 20% improvement in model accuracy
```

## 🔐 API Keys

The tool uses:
- **Firecrawl API**: For web scraping (included in setup)
- **Claude API**: For AI analysis (included in setup)

Your API keys are stored as environment variables after running the setup script.

## 💡 Tips for Best Results

1. **Use a text resume**: Save your resume as a .txt file for best parsing
2. **Be specific with roles**: Use exact job titles like "Senior Product Manager" or "ML Product Manager"
3. **Check multiple sources**: Use `--source multi` to get a broader market view
4. **Iterate**: Run the analysis periodically to track changing market demands

## 🐛 Troubleshooting

- **No jobs found**: Check your internet connection and API keys
- **API errors**: Ensure your API keys are valid and have sufficient credits
- **Missing dependencies**: Run the setup script or install packages manually

## 📈 Next Steps

After running the analysis:
1. Update your resume with suggested keywords
2. Add the AI-generated bullets to your experience section
3. Focus applications on companies with highest match scores
4. Address identified skill gaps through courses or projects

---

Built with ❤️ using Firecrawl and Claude AI