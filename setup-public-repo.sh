#!/usr/bin/env bash
# Run this on your Mac after cloning from the git bundle.
# Usage: ./setup-public-repo.sh

set -euo pipefail

REPO_NAME="career-command-center"
GITHUB_USER="${GITHUB_USER:-Dr1nkCoff33}"

echo "==> Career Command Center — publish to GitHub"
echo ""

if ! command -v gh &>/dev/null; then
  echo "Install GitHub CLI first: brew install gh && gh auth login"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "Run: gh auth login"
  exit 1
fi

# Ensure we're in a git repo with commits
if [[ ! -d .git ]]; then
  echo "Initializing git..."
  git init -b main
fi

if ! git rev-parse HEAD &>/dev/null; then
  echo "No commits yet. Stage files first:"
  echo "  git add . && git commit -m 'Initial public release'"
  exit 1
fi

# Remove bad remote if gh failed earlier
if git remote get-url origin &>/dev/null; then
  echo "Remote 'origin' already set:"
  git remote -v
  read -r -p "Push to this remote? [y/N] " ans
  if [[ "${ans,,}" == "y" ]]; then
    git push -u origin main
    echo "Done: https://github.com/${GITHUB_USER}/${REPO_NAME}"
    exit 0
  fi
fi

echo "Creating public repo ${GITHUB_USER}/${REPO_NAME}..."
gh repo create "${REPO_NAME}" \
  --public \
  --description "Portfolio + AI job-fit analyzer with CI/CD architecture proposal. Feedback welcome." \
  --source=. \
  --remote=origin \
  --push

echo ""
echo "Done! Share with colleagues:"
echo "  https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "  Architecture: Documentation/career-platform-architecture.md"
