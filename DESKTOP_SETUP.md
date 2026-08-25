# Publish from Cursor Desktop (Mac)

Your empty local folder failed because **the scrubbed files live in the Cloud Agent workspace**, not on your Mac yet. Use one of these methods.

---

## Method A — Git bundle (fastest, recommended)

### 1. Download the bundle from this Cloud Agent run

In Cursor Desktop, open **this agent conversation** → **Artifacts** (or agent output files):

- Download: **`career-command-center.bundle`**

### 2. On your Mac Terminal

```bash
cd ~/Documents/GitHub

# Clone from bundle (creates career-command-center/ with full history + all files)
git clone career-command-center.bundle career-command-center
cd career-command-center

# Publish to GitHub
chmod +x setup-public-repo.sh
./setup-public-repo.sh
```

If `gh repo create` says the repo already exists:

```bash
git remote add origin git@github.com:Dr1nkCoff33/career-command-center.git
# or: git@github.com:YOUR_USERNAME/career-command-center.git
git push -u origin main
```

---

## Method B — Copy folder from Cloud Agent in Cursor IDE

### 1. Open the Cloud Agent workspace

- Cursor → **Agents** → this conversation → open workspace / files

### 2. Copy the folder

Copy everything from:

```
career-command-center/
```

into:

```
~/Documents/GitHub/career-command-center/
```

**Do not copy** the inner `.git` folder if your Mac folder already has an empty `.git` — merge file contents only.

### 3. Commit and publish

```bash
cd ~/Documents/GitHub/career-command-center

# If you had an empty git init from before, that's fine — just add files:
git add .
git status    # MUST show README.md, job-analyzer-web/, Tools/, etc.

git commit -m "Initial public release: scrubbed Career Command Center"
git branch -M main

chmod +x setup-public-repo.sh
./setup-public-repo.sh
```

---

## Method C — From your Career repo (after branch is on GitHub)

If branch `cursor/career-command-center-public-a2e3` is pushed to GitHub:

```bash
cd ~/Documents/GitHub/Career
git fetch origin
git checkout cursor/career-command-center-public-a2e3

cp -r career-command-center-public/* ~/Documents/GitHub/career-command-center/
cd ~/Documents/GitHub/career-command-center

git init -b main
git add .
git commit -m "Initial public release"
./setup-public-repo.sh
```

---

## Verify before sharing publicly

```bash
cd ~/Documents/GitHub/career-command-center

# No API keys
grep -rE 'sk-ant-|fc-[a-f0-9]{20,}' . --exclude-dir=.git || echo "✓ No keys found"

# Has content
test -f README.md && test -d job-analyzer-web && echo "✓ Repo looks complete"
```

---

## After publish

1. **Enable Issues** on GitHub (feedback template included)
2. **Optional GitHub Pages:** Settings → Pages → branch `main`, folder `/docs`
3. Share: `Documentation/career-platform-architecture.md`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `no commits found` | Files not copied yet — run `git add .` after copying |
| `cd: /path/to/...` | Use `~/Documents/GitHub/career-command-center` |
| `repo already exists` | `git remote add origin git@github.com:USER/career-command-center.git && git push -u origin main` |
| `Bad credentials` | Run `gh auth login` |
