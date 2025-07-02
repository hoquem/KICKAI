# Railway Firebase Credentials Troubleshooting Guide

## 🚨 Critical Issue: Railway Environment Variable Corruption

This guide documents the solution to a persistent Firebase credentials issue that took an entire day to debug. The root cause was **Railway's environment variable handling corrupting large, complex strings with special characters**.

## Problem Symptoms

When deploying to Railway, you may encounter these errors:

```
- PEM file parsing errors
- "Invalid private key" errors
- Base64 environment variable size limits
- Truncated private keys
- Double-escaped newlines (`\\n`) instead of real newlines (`\n`)
```

## Root Cause Analysis

Railway has several limitations with environment variables:

1. **Size Limits**: Large environment variables get truncated
2. **Character Escaping**: Special characters like newlines get corrupted
3. **Variable Concatenation**: Multiple variables may get merged
4. **Base64 Issues**: Base64 encoding adds overhead and complexity

## ✅ The Solution

### Use `FIREBASE_CREDENTIALS_JSON` (Plain Text JSON)

**DO THIS:**
1. Download the original Firebase JSON file from Firebase Console
2. Set it as a single environment variable: `FIREBASE_CREDENTIALS_JSON`
3. Use real newlines, not base64 encoding
4. Keep the entire JSON in one variable

**DON'T DO THIS:**
- ❌ Split credentials into individual variables
- ❌ Use base64 encoding
- ❌ Use Railway secrets (size limits)
- ❌ Use Railway volumes (complex setup)

## Diagnostic Logging

The Firebase client now includes comprehensive diagnostic logging that will help identify Railway corruption:

### Corruption Indicators

The system will detect and log:
- `\\n` instead of real newlines
- Multiple PEM headers/footers
- Truncated private keys
- Empty or corrupted credentials

### Error Messages

When corruption is detected, you'll see messages like:
```
🚨 RAILWAY CORRUPTION DETECTED in FIREBASE_CREDENTIALS_JSON!
🔧 Found '\\n' instead of real newlines - Railway corrupted the environment variable
🔧 SOLUTION: Re-upload the original Firebase JSON file with real newlines
```

## Setup Instructions

### 1. Get Firebase Credentials
```bash
# Download from Firebase Console
# Project Settings > Service Accounts > Generate New Private Key
```

### 2. Set Railway Environment Variable
```bash
# In Railway dashboard or CLI
railway variables set FIREBASE_CREDENTIALS_JSON="<paste entire JSON here>"
```

### 3. Verify Setup
```bash
# Check the deployment logs
railway logs --service kickai-testing
```

## Common Mistakes to Avoid

### ❌ Individual Variables
```bash
# DON'T do this
railway variables set FIREBASE_PRIVATE_KEY="..."
railway variables set FIREBASE_CLIENT_EMAIL="..."
```

### ❌ Base64 Encoding
```bash
# DON'T do this
railway variables set FIREBASE_CREDENTIALS_BASE64="..."
```

### ❌ Railway Secrets
```bash
# DON'T do this - has size limits
railway secrets set FIREBASE_CREDENTIALS="..."
```

### ❌ Railway Volumes
```bash
# DON'T do this - complex and error-prone
railway volumes create firebase-creds
```

## Testing the Fix

### 1. Deploy to Testing
```bash
railway up --service kickai-testing
```

### 2. Check Logs
```bash
railway logs --service kickai-testing
```

### 3. Look for Success Messages
```
✅ Credentials created from JSON string (with PEM repair)
✅ Firebase app initialized successfully
✅ Firebase Firestore client created successfully
```

## Recovery Steps

If you encounter the issue again:

1. **Check the logs** for corruption indicators
2. **Re-upload** the original Firebase JSON file
3. **Verify** the environment variable contains the complete JSON
4. **Redeploy** the service

## Prevention

### For Future Deployments
1. Always use `FIREBASE_CREDENTIALS_JSON` as a single variable
2. Test credentials in staging before production
3. Monitor deployment logs for corruption indicators
4. Keep the original Firebase JSON file as backup

### Environment Variable Best Practices
1. Use plain text for complex JSON
2. Avoid splitting large variables
3. Test environment variables locally first
4. Document the exact format used

## Debugging Commands

### Check Environment Variables
```bash
# List all variables
railway variables

# Check specific variable
railway variables get FIREBASE_CREDENTIALS_JSON
```

### Monitor Deployments
```bash
# Watch deployment logs
railway logs --service kickai-testing --follow

# Check service status
railway status
```

### Test Locally
```bash
# Test with local environment
python -c "
import os
import json
creds = os.getenv('FIREBASE_CREDENTIALS_JSON')
if creds:
    data = json.loads(creds)
    print(f'Private key length: {len(data.get(\"private_key\", \"\"))}')
"
```

## Summary

The key lesson: **Railway environment variables are fragile with complex data**. Always use the simplest approach - a single plain text JSON variable with real newlines. The diagnostic logging will help you quickly identify and fix any future issues.

---

*This guide was created after a full day of debugging Railway Firebase credentials issues. The solution was to use `FIREBASE_CREDENTIALS_JSON` as a single environment variable with the original Firebase JSON file content.* 