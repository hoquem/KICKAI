#!/bin/bash

# Deploy to Railway Testing Environment
set -e

echo "🚀 Deploying to Railway Testing Environment..."

# Link to testing project
railway link --project kickai-testing

# Set environment variables
railway variables set ENVIRONMENT=testing
railway variables set RAILWAY_ENVIRONMENT=testing

# Deploy
railway up --environment testing

echo "✅ Successfully deployed to testing environment!" 