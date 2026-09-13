# Career Command Center — Architecture Overview

> **Purpose:** Shareable architecture for review. This doc describes how GitHub Actions, Buildkite, Vercel, and Google Cloud work together to power a career portfolio + AI job-fit platform.
>
> **Feedback welcome on:** service boundaries, over-engineering, security, cost, and whether this tells a credible CI/CD story.

---

## 1. System context (who talks to what)

```mermaid
flowchart TB
    subgraph Users["Users"]
        U1["Job seeker / you"]
        U2["Recruiter / reviewer"]
        U3["Engineering friend (this doc)"]
    end

    subgraph Platform["Career Command Center"]
        WEB["Web app<br/>(Next.js)"]
        API["Analyzer API<br/>(Python / FastAPI)"]
        DATA["Data & artifacts"]
        CICD["CI/CD pipelines"]
    end

    subgraph External["External services"]
        CLAUDE["Claude API<br/>(Anthropic)"]
        FIRECRAWL["Firecrawl<br/>(job scraping)"]
        GH["GitHub<br/>(source + PRs)"]
    end

    U1 --> WEB
    U2 --> WEB
    U3 --> GH

    WEB --> API
    API --> CLAUDE
    API --> FIRECRAWL
    API --> DATA

    GH --> CICD
    CICD --> WEB
    CICD --> API
    CICD --> DATA
```

---

## 2. Deployment topology (where things run)

```mermaid
flowchart LR
    subgraph GitHub["GitHub"]
        REPO["carlos-jvr-mrtn/Career<br/>Resume/ · Tools/ · agents/<br/>job-analyzer-web/ · Analysis/"]
        GHA["GitHub Actions<br/>PR gates"]
    end

    subgraph Buildkite["Buildkite"]
        BK["Pipeline orchestrator"]
        AGENTS["Agents on GCE / GKE<br/>(Docker builds, tests, deploy)"]
    end

    subgraph Vercel["Vercel"]
        NEXT["job-analyzer-web<br/>Next.js 14"]
        EDGE["Edge / API routes<br/>(lightweight)"]
        PREVIEW["Preview URLs<br/>(per PR)"]
    end

    subgraph GCP["Google Cloud"]
        CR["Cloud Run<br/>Analyzer API"]
        CRJ["Cloud Run Jobs<br/>(nightly scrape)"]
        SCH["Cloud Scheduler"]
        GCS["Cloud Storage<br/>(resumes, reports)"]
        SM["Secret Manager"]
        AR["Artifact Registry<br/>(Docker images)"]
        FS["Firestore<br/>(app tracker)"]
    end

    REPO --> GHA
    GHA -->|"merge to main"| BK
    BK --> AGENTS
    AGENTS --> AR
    AGENTS -->|"deploy frontend"| NEXT
    AGENTS -->|"deploy API image"| CR

    NEXT --> EDGE
    EDGE -->|"heavy analysis"| CR
    CR --> GCS
    CR --> FS
    CR --> SM
    CR --> CLAUDE_EXT["Claude API"]
    CR --> FC_EXT["Firecrawl"]

    SCH --> CRJ
    CRJ --> GCS
    CRJ --> REPO

    PREVIEW -.->|"PR branch"| NEXT
```

---

## 3. CI/CD pipeline (the Harness-CI-style story)

```mermaid
flowchart TD
    START(["Developer pushes / opens PR"]) --> GHA

    subgraph GHA["GitHub Actions — fast feedback (~1–3 min)"]
        LINT["Lint TS + markdown"]
        TYPE["Type-check Next.js"]
        PYTEST["pytest: Tools/ + agents/"]
        SEC["Dependency / secret scan"]
    end

    GHA -->|"✅ all checks pass"| MERGE{"Merge to main?"}
    MERGE -->|No| PREVIEW["Vercel preview deploy<br/>(optional, from PR)"]
    MERGE -->|Yes| BK_TRIGGER

    BK_TRIGGER["Buildkite triggered"] --> BK_TEST

    subgraph BK_TEST["Buildkite — Test stage (parallel)"]
        T1["Next.js build + smoke test"]
        T2["Python integration tests"]
        T3["Docker image lint"]
    end

    BK_TEST --> BK_BUILD

    subgraph BK_BUILD["Buildkite — Build stage"]
        DOCKER["docker build job-analyzer-web"]
        PUSH["push → Artifact Registry"]
    end

    BK_BUILD --> BK_DEPLOY

    subgraph BK_DEPLOY["Buildkite — Deploy stage"]
        STG["Deploy API → Cloud Run (staging)"]
        GATE{"Manual unblock?"}
        PROD_API["Promote API → Cloud Run (prod)"]
        PROD_WEB["Trigger Vercel production deploy"]
    end

    BK_DEPLOY --> STG --> GATE
    GATE -->|Approve| PROD_API
    GATE -->|Approve| PROD_WEB

    subgraph NIGHTLY["Nightly (Cloud Scheduler → Buildkite or Run Job)"]
        SCRAPE["Run firecrawl_job_scraper.py"]
        ANALYZE["Run job_market_analyzer.py"]
        COMMIT["Write Analysis/ → GCS + optional git commit"]
    end

    PROD_API --> NIGHTLY
```

---

## 4. Request flow — “Analyze my resume”

```mermaid
sequenceDiagram
    actor User
    participant Vercel as Vercel (Next.js)
    participant API as Cloud Run (FastAPI)
    participant GCS as Cloud Storage
    participant Claude as Claude API
    participant FC as Firecrawl
    participant FS as Firestore

    User->>Vercel: Upload resume + select company/locations
    Vercel->>Vercel: Validate input, auth (optional)

    alt Lightweight / demo mode
        Vercel->>Claude: Direct call (sample jobs)
        Claude-->>Vercel: Match scores + gaps
    else Production mode
        Vercel->>API: POST /analyze (resume, company, locations)
        API->>FC: Fetch live job postings (cache TTL)
        FC-->>API: Job descriptions
        API->>API: semantic_matcher.py scoring
        API->>Claude: Gap analysis + suggestions
        Claude-->>API: Structured JSON
        API->>GCS: Store analysis artifact (optional)
        API->>FS: Upsert application tracker row (optional)
        API-->>Vercel: AnalysisResult JSON
    end

    Vercel-->>User: Results page + charts
```

---

## 5. Product surfaces (what users see)

```mermaid
flowchart TB
    subgraph Site["career.yourdomain.com (Vercel)"]
        HOME["/ — Portfolio & about"]
        ANALYZER["/analyzer — Job Fit Analyzer"]
        TRACKER["/tracker — Application pipeline"]
        MARKET["/market — Skills trends dashboard"]
        CI["/about/ci — Live pipeline status"]
    end

    subgraph Backend["Backend capabilities (GCP)"]
        B1["Live job scraping"]
        B2["Semantic resume matching"]
        B3["Nightly market reports"]
        B4["Versioned resume storage"]
    end

    HOME --> CI
    ANALYZER --> B1
    ANALYZER --> B2
    TRACKER --> B4
    MARKET --> B3
    CI --> BK_STATUS["Buildkite badge / API"]
```

---

## 6. Component responsibilities

| Layer | Tool | Responsibility | Runs when |
|-------|------|----------------|-----------|
| Source | **GitHub** | Repo, PRs, code review | Always |
| PR gates | **GitHub Actions** | Lint, type-check, unit tests, security | Every push / PR |
| Orchestration | **Buildkite** | Multi-stage pipelines, Docker builds, deploys, nightly jobs | Merge to main + schedule |
| Frontend | **Vercel** | Next.js UI, previews, edge routes | Every request |
| API | **GCP Cloud Run** | Python analyzers, scraping, Claude orchestration | On demand |
| Batch | **GCP Cloud Run Jobs** | Nightly scrape + analyze | Cron (e.g. 2am PT) |
| Storage | **GCS** | Resumes, JSON/Markdown reports | On write |
| Secrets | **Secret Manager** | Claude, Firecrawl keys | On API start |
| Tracker | **Firestore** | Application stages, notes | On user action |
| Images | **Artifact Registry** | Container images from Buildkite | On build |

---

## 7. Repo → service mapping (today → target)

| Repo path | Today | Target home |
|-----------|-------|-------------|
| `job-analyzer-web/` | Local dev | **Vercel** (production + previews) |
| `Tools/*.py`, `agents/` | CLI / scripts | **Cloud Run** (FastAPI wrapper) |
| `Analysis/` | Committed markdown/JSON | **GCS** (+ optional git sync) |
| `Resume/` | Static files in repo | **GCS** (versioned) + links from Vercel |
| _(static portfolio page)_ | Static portfolio | Merged into Next.js `/` |
| `Dockerfile` | Local compose | Built by **Buildkite** → **Artifact Registry** → **Cloud Run** |

---

## 8. Security & data boundaries

```mermaid
flowchart LR
    subgraph Public["Public edge"]
        VERCEL["Vercel"]
    end

    subgraph Private["Private / authenticated"]
        CR["Cloud Run API"]
        SM["Secret Manager"]
    end

    subgraph Data["Data at rest"]
        GCS["GCS — encrypted"]
        FS["Firestore — rules"]
    end

    VERCEL -->|"HTTPS only, no secrets in client"| CR
    CR --> SM
    CR --> GCS
    CR --> FS

    NOTE["Resume data: in-memory during analysis;<br/>optional persist to GCS with TTL.<br/>API keys never in browser (prod)."]
```

**Key decisions for review:**
- Client-side Claude API key (current demo) vs server-side only (production)
- Whether to persist resumes or keep ephemeral-only
- Firestore vs flat files in GCS for application tracker
- Public `/about/ci` page exposing Buildkite pipeline metadata

---

## 9. Cost & complexity (honest take)

| Phase | Stack | Monthly ballpark | Complexity |
|-------|-------|------------------|------------|
| **MVP** | Vercel + GitHub Actions only | $0–20 | Low |
| **Phase 2** | + Cloud Run API + Secret Manager | $5–30 | Medium |
| **Full** | + Buildkite + Scheduler + GCS + Firestore | $30–100+ | High |

**Recommendation:** Ship Vercel + GitHub Actions first. Add Buildkite when you want the CI/CD portfolio story. Add GCP when live scraping replaces hardcoded sample jobs.

---

## 10. Questions for reviewers

1. **Boundaries:** Should the Next.js `/api/analyze` route stay on Vercel, or should all analysis move to Cloud Run immediately?
2. **Buildkite vs Actions:** Is Buildkite overkill if GitHub Actions can build Docker and deploy to Cloud Run? (Tradeoff: Buildkite is better for complex pipelines + your PM narrative.)
3. **Data:** Ephemeral resume processing only, or versioned storage in GCS?
4. **Nightly jobs:** Buildkite scheduled pipeline vs Cloud Scheduler → Cloud Run Job — preference?
5. **Scope:** Which product surface is highest value — Analyzer, Tracker, or Market dashboard?
6. **Security:** Anything alarming about the Claude/Firecrawl integration pattern?

---

## 11. One-page summary (copy/paste for Slack)

```
Career Command Center
─────────────────────
GitHub repo → GitHub Actions (PR lint/test) → Buildkite (build/deploy)
                                                    ├→ Vercel (Next.js UI)
                                                    └→ GCP Cloud Run (Python API)
                                                           ├→ Claude + Firecrawl
                                                           ├→ GCS (artifacts)
                                                           └→ Firestore (tracker)

Nightly: Cloud Scheduler → scrape jobs → update Analysis/ + market dashboard
Public site: portfolio + job analyzer + application tracker + live CI status page
```

---

*Generated from the Career repo architecture proposal. Render mermaid diagrams on GitHub or at [mermaid.live](https://mermaid.live).*
