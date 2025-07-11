#!/bin/bash

# Deploy to Railway Production Environment
set -e

echo "🚀 Deploying to Railway Production Environment..."

# Link to production project
railway link --project kickai-production

# Set environment variables
railway variables set ENVIRONMENT=production
railway variables set RAILWAY_ENVIRONMENT=production

# Deploy
railway up --environment production

echo "✅ Successfully deployed to production environment!" 