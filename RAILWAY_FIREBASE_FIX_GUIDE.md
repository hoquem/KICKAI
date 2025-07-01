# Railway Firebase Credentials Fix Guide

## 🚨 Current Issue

The Firebase credentials are failing because Railway CLI is escaping newlines in the JSON (`\\n` instead of `\n`), causing PEM parsing errors.

## ✅ Railway's Official Solution

Railway officially recommends using **Railway's dashboard** for large sensitive data, not CLI commands.

### Step 1: Remove Problematic Variables

First, let's clear the problematic variables:

```bash
# Set empty values to clear the problematic variables
railway variables --set "FIREBASE_CREDENTIALS_JSON=" --service kickai-testing
railway variables --set "FIREBASE_CREDENTIALS_JSON=" --service kickai-staging  
railway variables --set "FIREBASE_CREDENTIALS_JSON=" --service kickai-production
```

### Step 2: Use Railway Dashboard (Official Approach)

1. **Open Railway Dashboard**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Select your project
   - Go to each service (testing, staging, production)

2. **Add Secret Variable**
   - Click on the service (e.g., `kickai-testing`)
   - Go to **Variables** tab
   - Click **New Variable**
   - Set **Name**: `FIREBASE_CREDENTIALS_JSON`
   - Set **Value**: Copy the entire content of the corresponding JSON file:
     - `firebase-credentials-testing.json` for testing
     - `firebase-credentials-staging.json` for staging  
     - `firebase-credentials-production.json` for production
   - **Important**: Make sure to copy the raw JSON content, not escaped

3. **Verify Setup**
   - The variable should be marked as **Secret** (hidden from logs)
   - The JSON should have proper `\n` newlines, not `\\n`

### Step 3: Deploy and Test

```bash
# Deploy testing environment
railway up --service kickai-testing

# Check logs
railway logs --service kickai-testing
```

## 🔧 Alternative: Use Individual Environment Variables

If the dashboard approach doesn't work, we can use individual environment variables:

```bash
# Set individual variables (non-sensitive data only)
railway variables --set "FIREBASE_PROJECT_ID=kickai-954c2" --service kickai-testing
railway variables --set "FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@kickai-954c2.iam.gserviceaccount.com" --service kickai-testing

# For the private key, use base64 encoding to avoid escaping issues
base64 -i firebase-credentials-testing.json | railway variables --set "FIREBASE_CREDENTIALS_B64=$(cat -)" --service kickai-testing
```

Then update the Firebase client to decode base64:

```python
# In firebase_tools.py
import base64
firebase_creds_b64 = os.getenv('FIREBASE_CREDENTIALS_B64')
if firebase_creds_b64:
    firebase_creds_json = base64.b64decode(firebase_creds_b64).decode('utf-8')
```

## 📋 Current Status

- ✅ Firebase client updated to use `FIREBASE_CREDENTIALS_JSON`
- ✅ Railway configuration updated
- ✅ Credentials files created
- ❌ **Issue**: CLI escaping newlines in JSON
- 🔧 **Solution**: Use Railway dashboard for secrets

## 🎯 Next Steps

1. **Use Railway Dashboard** to set `FIREBASE_CREDENTIALS_JSON` properly
2. **Deploy testing environment** to verify Firebase connection
3. **Check logs** for successful Firebase initialization
4. **Repeat for staging and production** environments

## 🔍 Verification

After setting up, check the logs for:
```
✅ Firebase app initialized with Railway dashboard credentials
✅ Firebase Firestore client created successfully
```

If you see these messages, the Firebase connection is working correctly! 