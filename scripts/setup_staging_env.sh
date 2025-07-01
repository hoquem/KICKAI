#!/bin/bash
# Environment Variables Setup Script for Staging

echo "🔧 Setting up environment variables for staging..."

# Set bot token for staging (you'll need to provide this)
echo "Please provide the staging bot token:"
read -s STAGING_BOT_TOKEN

if [ -z "$STAGING_BOT_TOKEN" ]; then
    echo "❌ No bot token provided"
    exit 1
fi

# Set the bot token in Railway
railway variables --service kickai-staging --set TELEGRAM_BOT_TOKEN="$STAGING_BOT_TOKEN"

if [ $? -eq 0 ]; then
    echo "✅ Staging bot token set successfully"
else
    echo "❌ Failed to set staging bot token"
    exit 1
fi

echo "🎉 Staging environment variables setup completed!"
