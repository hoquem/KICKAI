#!/bin/bash

# Use first argument as project ID if provided, otherwise try to auto-detect
if [ -n "$1" ]; then
  PROJECT_ID="$1"
else
  PROJECT_ID=$(railway status --json 2>/dev/null | grep -o '"projectId":"[^"]*' | cut -d':' -f2 | tr -d '"')
fi

if [ -z "$PROJECT_ID" ]; then
  echo "❌ Could not auto-detect Railway project ID. Are you in a Railway project directory?"
  echo "You can manually specify the project ID: ./sync_env_from_railway.sh <project_id>"
  exit 1
fi

echo "🔍 Using Railway project ID: $PROJECT_ID"

# You can change the environment below if you want (e.g., production, staging, development)
ENVIRONMENT="production"

echo "⬇️  Fetching Railway environment variables for project: $PROJECT_ID (env: $ENVIRONMENT) ..."

railway env pull "$ENVIRONMENT" "$PROJECT_ID" .env

if [ $? -eq 0 ]; then
  echo "✅ Synced Railway variables to .env"
else
  echo "❌ Failed to fetch variables from Railway"
  exit 1
fi 