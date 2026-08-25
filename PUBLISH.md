# Publish this repo to GitHub (one-time)

The scrubbed public repo is ready in this directory. Run these commands from your machine (with `gh` authenticated):

```bash
cd career-command-center

# Create public repo and push
gh repo create career-command-center \
  --public \
  --description "Portfolio + AI job-fit analyzer with CI/CD architecture proposal. Feedback welcome." \
  --source=. \
  --remote=origin \
  --push
```

If the repo name is taken, pick another (e.g. `career-command-center-public`) and update links in `README.md` and `CONTRIBUTING.md`.

## Verify before publishing

```bash
# Confirm no secrets slipped in
grep -rE 'sk-ant-|fc-[a-f0-9]{20,}|@[a-z]+\.[a-z]+' . \
  --exclude-dir=.git --exclude='PUBLISH.md' || echo "Clean"

# Confirm sensitive folders are absent
test ! -d References && test ! -d Analysis && echo "Sensitive dirs excluded"
```

## After publish

1. Enable **Issues** on the repo (for feedback template)
2. Optional: enable **GitHub Pages** from `/docs` for portfolio + architecture HTML
3. Share: `https://github.com/YOUR_USER/career-command-center`
4. **Rotate** Firecrawl and Claude API keys if the private Career repo was ever shared (old keys may be in that repo's history)

## What was scrubbed vs private Career repo

| Removed | Kept |
|---------|------|
| Annual performance reviews | Architecture docs |
| Real job analyses & Job-Roles | job-analyzer-web app |
| Hardcoded API keys | Python tools (env vars only) |
| Phone, email, street address | LinkedIn + redacted resume |
| Test scripts with embedded keys | Sample analysis example |
