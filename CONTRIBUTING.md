# Contributing

Thanks for reviewing or contributing to Career Command Center.

## What we're looking for

This project is open for **architecture and product feedback**, especially on:

- CI/CD pipeline design (GitHub Actions, Buildkite, Vercel, GCP)
- Service boundaries (edge API vs Cloud Run backend)
- Security model for resume processing
- Scope and rollout phases

See [Documentation/career-platform-architecture.md](Documentation/career-platform-architecture.md) and the reviewer questions at the end of that doc.

## How to give feedback

- Open a [GitHub Issue](https://github.com/Dr1nkCoff33/career-command-center/issues) with label `feedback`
- Comment on an existing issue if one matches your topic
- For small fixes, open a PR against `main`

## Local setup

```bash
# Python tools
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your own API keys

# Web app
cd job-analyzer-web
npm install
cp .env.example .env.local
npm run dev
```

## Code guidelines

- No API keys or credentials in source code — use environment variables only
- Keep imports at the top of files
- Match existing style in the module you're editing
