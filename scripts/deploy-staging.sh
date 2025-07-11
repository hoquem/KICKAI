#!/bin/bash

# Deploy to Railway Staging Environment
set -e

echo "🚀 Deploying to Railway Staging Environment..."

# Link to staging project
railway link --project kickai-staging

# Set environment variables
railway variables set ENVIRONMENT=staging
railway variables set RAILWAY_ENVIRONMENT=staging

# Deploy
railway up --environment staging

echo "✅ Successfully deployed to staging environment!" 