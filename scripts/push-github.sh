#!/usr/bin/env bash
# Push this monorepo to a GitHub repo.
#
# Usage:
#   ./scripts/push-github.sh https://github.com/USERNAME/autotune-ai.git
#   ./scripts/push-github.sh git@github.com:USERNAME/autotune-ai.git
#
# Prerequisites:
#   - You've created an EMPTY repo at that URL.
#   - You're authenticated: `gh auth login` OR your SSH key is added to GitHub.

set -euo pipefail
cd "$(dirname "$0")/.."

REPO_URL="${1:-}"
if [ -z "$REPO_URL" ]; then
  echo "Usage: $0 <https-or-ssh-github-url>"
  exit 1
fi

if [ ! -d .git ]; then
  echo "→ git init"
  git init -q
  git branch -M main
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "→ adding origin = $REPO_URL"
  git remote add origin "$REPO_URL"
else
  echo "→ updating origin = $REPO_URL"
  git remote set-url origin "$REPO_URL"
fi

# Make sure we never commit local secrets or state
cat > .git/info/exclude <<'EOF'
.env
.venv/
node_modules/
.next/
data/
tmp/
EOF

# Stage everything the .gitignore allows
git add -A

if git diff --cached --quiet; then
  echo "→ nothing new to commit"
else
  git commit -q -m "chore: initial AutoTune AI monorepo

Backend (FastAPI + Celery), shared schemas (Pydantic + Zod),
web dashboard (Next.js 16), mobile (Expo + expo-router),
AI orchestrator (multi-agent + tool use), A2L parser + KB ingest,
ECU protocol simulator, TOTP MFA, ed25519 signing,
K8s manifests + Terraform for AWS, CI + release workflows,
business docs (roadmap, pitch, financials, deploy)."
fi

echo "→ pushing to origin/main…"
git push -u origin main

REPO_HTTPS=$(echo "$REPO_URL" | sed -E 's#^git@github.com:#https://github.com/#; s#\.git$##')
echo
echo "════════════════════════════════════════════════════════════════"
echo " ✓ Pushed to $REPO_HTTPS"
echo
echo " Next: deploy the web app to Vercel"
echo "   https://vercel.com/new  →  import ${REPO_HTTPS}"
echo "   or:  vercel   (from this directory)"
echo
echo " Read docs/DEPLOY.md for the full deployment guide."
echo "════════════════════════════════════════════════════════════════"
