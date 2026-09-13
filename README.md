# Career Command Center

A public portfolio and tooling project that combines an AI-powered job-fit analyzer, CI/CD architecture proposal, and PM career site.

**Looking for feedback?** Start with the [architecture overview](Documentation/career-platform-architecture.md) or open an issue.

---

## What's in this repo

| Area | Description |
|------|-------------|
| **[job-analyzer-web/](job-analyzer-web/)** | Next.js 14 app — upload a resume, pick a company, get match scores and gap analysis |
| **[Tools/](Tools/)** | Python CLI for job scraping (Firecrawl) and AI analysis (Claude) |
| **[agents/](agents/)** | Semantic matching with BERTopic for resume–job alignment |
| **[Documentation/](Documentation/)** | Architecture doc (Buildkite, GitHub Actions, Vercel, GCP) + tool README |
| **[docs/](docs/)** | Portfolio landing page + architecture HTML viewer |

---

## Architecture (seeking review)

Proposed platform design using **GitHub Actions**, **Buildkite**, **Vercel**, and **Google Cloud**:

- **GitHub Actions** — fast PR checks (lint, test, security)
- **Buildkite** — multi-stage pipelines, Docker builds, deploys
- **Vercel** — Next.js frontend and preview deployments
- **GCP** — Cloud Run API, scheduled scraping jobs, artifact storage

Read the full doc: **[Documentation/career-platform-architecture.md](Documentation/career-platform-architecture.md)**

Browser version: **[docs/career-platform-architecture.html](docs/career-platform-architecture.html)**

---

## Quick start

### Web app

```bash
cd job-analyzer-web
npm install
npm run dev
# → http://localhost:3000
```

Optional: add `CLAUDE_API_KEY` to `.env.local` for server-side analysis.

### Python CLI

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add FIRECRAWL_API_KEY and CLAUDE_API_KEY

cd Tools
python job_analyzer_cli.py --role "Product Manager" --source meta
```

### Analyze a single job URL

```bash
python analyze_single_job.py "https://example.com/job-posting" /path/to/your-resume.md
```

---

## Project structure

```
career-command-center/
├── job-analyzer-web/       # Next.js frontend + API routes
├── Tools/                  # Python scraping and analysis CLI
├── agents/                 # Semantic matching agents
├── Documentation/          # Architecture + tool docs
├── docs/                   # Static portfolio + architecture HTML
├── Resume/                 # Public resume
├── examples/               # Sample analyzer output
└── workflows/              # Workflow descriptions
```

---

## Feedback welcome

This repo is public so engineers can critique the architecture and product direction. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for how to share feedback.

Key questions we're exploring:

1. Should analysis stay on Vercel edge routes or move to Cloud Run?
2. Is Buildkite worth it vs GitHub Actions for Docker + deploy?
3. Ephemeral resume processing vs versioned storage in GCS?
4. Which surface is highest value: Analyzer, Application Tracker, or Market Dashboard?

---

## License

MIT — see [LICENSE](LICENSE).
