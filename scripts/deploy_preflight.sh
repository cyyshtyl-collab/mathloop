#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.deploy.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .deploy.env. Copy .deploy.env.example to .deploy.env and fill credentials."
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

required=(
  GITHUB_REPO
  FRONTEND_DOMAIN
  BACKEND_DOMAIN
  IMAGE_DOMAIN
  VERCEL_TOKEN
  CLOUDFLARE_API_TOKEN
  CLOUDFLARE_ACCOUNT_ID
  CLOUDFLARE_ZONE_ID
  R2_BUCKET
  S3_ENDPOINT_URL
  S3_ACCESS_KEY_ID
  S3_SECRET_ACCESS_KEY
  JWT_SECRET_KEY
)

missing=()
for key in "${required[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    missing+=("$key")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "Missing required values:"
  printf ' - %s\n' "${missing[@]}"
  exit 1
fi

echo "Deploy preflight OK."
echo "Frontend: https://$FRONTEND_DOMAIN"
echo "Backend:  https://$BACKEND_DOMAIN"
echo "Images:   https://$IMAGE_DOMAIN"
