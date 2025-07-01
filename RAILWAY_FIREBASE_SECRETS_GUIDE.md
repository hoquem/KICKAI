# Railway Firebase Secrets Management Guide

## Overview

This guide explains how to properly store Firebase credentials in Railway using their **official secrets management** approach. Railway environment variables have size limits that cause PEM file truncation issues, so we use Railway's recommended solution.

## Railway's Official Recommendation

Railway officially recommends:
1. **Store non-sensitive data as environment variables** (project ID, client email, etc.)
2. **Store sensitive data through Railway dashboard** (private keys, full credentials JSON)
3. **Use Railway's built-in secrets management** for large files

## Current Setup Status

✅ **Environment variables set for all environments:**
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL` 
- `FIREBASE_PRIVATE_KEY_ID`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_AUTH_URI`
- `FIREBASE_TOKEN_URI`
- `FIREBASE_AUTH_PROVIDER_X509_CERT_URL`
- `FIREBASE_CLIENT_X509_CERT_URL`

## Manual Steps Required

### Option 1: Add FIREBASE_CREDENTIALS_JSON Secret (Recommended)

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

3. **Verify Setup**
   - The variable should be marked as **Secret** (hidden from logs)
   - Deploy the service to test Firebase connection

### Option 2: Use Railway File Upload (Alternative)

1. **Upload Credentials File**
   - In Railway dashboard, go to **Variables** tab
   - Use Railway's file upload feature
   - Upload the credentials JSON file

2. **Set Path Variable**
   - Add `FIREBASE_CREDENTIALS_PATH` pointing to uploaded file
   - Example: `/app/uploads/firebase-credentials.json`

## Firebase Client Priority Order

The Firebase client follows this priority order:

1. **`FIREBASE_CREDENTIALS_JSON`** (Railway dashboard secret) ⭐ **Recommended**
2. **`FIREBASE_CREDENTIALS_PATH`** (Railway file upload)
3. **Environment variables** (legacy approach)
4. **`FIREBASE_CREDENTIALS`** (fallback)
5. **Local files** (development only)

## Benefits of This Approach

✅ **No size limits** - Railway secrets can handle large JSON files
✅ **Secure** - Secrets are encrypted and hidden from logs
✅ **Official** - Follows Railway's recommended practices
✅ **Reliable** - No more PEM file truncation issues
✅ **Scalable** - Works for all environments

## Troubleshooting

### Common Issues

1. **"Missing FIREBASE_PRIVATE_KEY" error**
   - Solution: Add `FIREBASE_CREDENTIALS_JSON` secret in Railway dashboard

2. **"PEM file parsing error"**
   - Solution: Use Railway secrets instead of environment variables

3. **"Firebase credentials not found"**
   - Solution: Check that `FIREBASE_CREDENTIALS_JSON` is set correctly

### Verification Commands

```bash
# Check Railway variables
railway variables --service kickai-testing

# Deploy and check logs
railway up --service kickai-testing
railway logs --service kickai-testing
```

## Files Created

- `firebase-credentials-testing.json` - For testing environment
- `firebase-credentials-staging.json` - For staging environment  
- `firebase-credentials-production.json` - For production environment

## Next Steps

1. **Add secrets to Railway dashboard** (manual step)
2. **Deploy services** to test Firebase connection
3. **Verify logs** show successful Firebase initialization
4. **Test bot functionality** with Firebase operations

## Security Notes

- ✅ Credentials files are generated locally and should be deleted after upload
- ✅ Railway secrets are encrypted and secure
- ✅ No sensitive data in environment variables
- ✅ Follows Railway's security best practices

---

**Status**: ✅ Environment variables set, 🔧 Manual secrets setup required 