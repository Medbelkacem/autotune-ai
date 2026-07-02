# Deployment Guide

## Overview

AutoTune AI has **two deployables**:

| Component | Where it runs on Vercel? | Notes |
|---|---|---|
| **`apps/web`** (Next.js dashboard) | ✅ Yes | Native Vercel target. |
| **`apps/mobile`** (Expo/React Native) | ❌ No | Ship via EAS / TestFlight / Play Store. |
| **`services/api`** (FastAPI) | ❌ No (long-lived container) | Deploy to Render / Fly.io / Railway / AWS ECS / Kubernetes. |
| **`services/analysis-worker`** (Celery) | ❌ No | Same as API — needs a persistent worker. |
| Postgres / Redis / RabbitMQ | ❌ No | Use managed services (Neon, Upstash, CloudAMQP) or self-host. |

So the natural production topology is:
- **Vercel** → Next.js frontend
- **Managed cloud** (Fly.io / Render / Railway / AWS) → FastAPI + Celery
- **Managed data** (Neon Postgres w/ pgvector, Upstash Redis, CloudAMQP)

---

## Push to GitHub

```bash
cd /home/free/Desktop/auto
./scripts/push-github.sh https://github.com/YOUR_USERNAME/autotune-ai.git
```

The script:
1. `git init`s the repo (if not already)
2. Creates a `main` branch
3. Adds all files (excluding `.env`, `.venv`, `node_modules`)
4. Creates the first commit
5. Pushes to the URL you passed

Prerequisites:
- `gh auth login` OR SSH key already registered with GitHub
- Empty repo already created at the URL

---

## Deploy the web app to Vercel

### Option A — Vercel CLI (recommended)

```bash
# one-time
npm i -g vercel
vercel login

# deploy
cd /home/free/Desktop/auto
vercel                  # first time → answers below
```

When prompted:

| Prompt | Answer |
|---|---|
| Set up and deploy? | **Y** |
| Which scope? | your account |
| Link to existing project? | **N** |
| Project name? | `autotune-ai` |
| In which directory is your code located? | `./` (root — pnpm workspace lives here) |
| Modify settings? | **N** |

Vercel auto-detects Next.js, honors `vercel.json` and `pnpm-workspace.yaml`, and installs from the workspace root.

### Option B — GitHub → Vercel dashboard

1. Push to GitHub (see above).
2. Go to https://vercel.com/new
3. Import your repo. Vercel reads `vercel.json` and Next.js is picked up automatically.
4. Set the environment variables below.
5. Click **Deploy**.

### Required Vercel env vars

Set these in **Project Settings → Environment Variables**:

| Name | Value | Env |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-api.fly.dev` (URL of the deployed FastAPI) | All |
| `NEXTAUTH_URL` | `https://YOUR-VERCEL-URL` | Production, Preview |
| `NEXTAUTH_SECRET` | 32-byte random string | All |

After first deploy the web app is live at `https://autotune-ai.vercel.app`.

---

## Deploy the API (Fly.io — simplest)

```bash
# one-time
curl -L https://fly.io/install.sh | sh
fly auth login

cd /home/free/Desktop/auto
fly launch --dockerfile services/api/Dockerfile --no-deploy
# accept name, region iad; skip Postgres (we'll use Neon)
```

Add secrets:

```bash
fly secrets set \
  SECRET_KEY="$(openssl rand -base64 32)" \
  DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/autotune?sslmode=require" \
  REDIS_URL="rediss://default:pass@dragonfly-xxx.upstash.io:6379" \
  RABBITMQ_URL="amqps://user:pass@octopus-01.rmq.cloudamqp.com:5671/vhost" \
  CELERY_BROKER_URL="$(fly secrets show RABBITMQ_URL)" \
  CELERY_RESULT_BACKEND="$(fly secrets show REDIS_URL)" \
  ANTHROPIC_API_KEY="sk-ant-…" \
  PASSWORD_PEPPER="$(openssl rand -base64 24)"

fly deploy
```

Then set `NEXT_PUBLIC_API_URL=https://autotune-api.fly.dev` in Vercel.

---

## Managed data services

| Service | Free tier | Notes |
|---|---|---|
| **Neon** (Postgres + pgvector) | Yes | pgvector enabled by default; run Alembic against it. |
| **Upstash** (Redis) | Yes | REST + TCP; use TCP URL for Celery. |
| **CloudAMQP** (RabbitMQ) | Yes (Little Lemur) | 1M msgs/mo free. |
| **Cloudflare R2** or **Backblaze B2** | Yes | S3-compatible object storage. |
| **Qdrant Cloud** | 1GB free | For high-recall vector search. |

---

## Post-deploy checklist

- [ ] `curl https://autotune-api.fly.dev/v1/healthz` returns 200
- [ ] Vercel deployment URL loads the landing page
- [ ] Signup at `/login` creates an org and returns tokens
- [ ] `alembic upgrade head` was run (once) against the Neon DB
- [ ] Seed data loaded: `python -m app.scripts.seed`
- [ ] KB seed loaded: `python -m app.scripts.ingest_seed_kb`
- [ ] TOTP works end-to-end (enroll + verify + login)
- [ ] `/v1/ai/ask` returns an answer with citations
