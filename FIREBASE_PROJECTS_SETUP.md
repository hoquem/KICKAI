# Firebase Projects Setup Guide

## 🎯 **Goal: Separate Firebase Projects for Each Environment**

This guide will help you set up separate Firebase projects for testing, staging, and production environments.

## 📋 **Project Structure**

```
Firebase Projects:
├── kickai-testing     (for testing environment)
├── kickai-staging     (for staging environment)  
└── kickai-production  (for production environment)
```

## 🚀 **Step 1: Create Firebase Projects**

### **1.1 Go to Firebase Console**
- Visit: https://console.firebase.google.com/
- Sign in with your Google account

### **1.2 Create Testing Project**
1. Click **"Add project"**
2. **Project name**: `kickai-testing`
3. **Project ID**: `kickai-testing` (or auto-generated)
4. **Google Analytics**: Disable (optional)
5. Click **"Create project"**

### **1.3 Create Staging Project**
1. Click **"Add project"**
2. **Project name**: `kickai-staging`
3. **Project ID**: `kickai-staging` (or auto-generated)
4. **Google Analytics**: Disable (optional)
5. Click **"Create project"**

### **1.4 Create Production Project**
1. Click **"Add project"**
2. **Project name**: `kickai-production`
3. **Project ID**: `kickai-production` (or auto-generated)
4. **Google Analytics**: Enable (recommended for production)
5. Click **"Create project"**

## 🔥 **Step 2: Enable Firestore Database**

For each project:

### **2.1 Navigate to Firestore**
1. In Firebase Console, select your project
2. Click **"Firestore Database"** in the left sidebar
3. Click **"Create database"**

### **2.2 Choose Security Rules**
1. **Start in test mode** (for now)
2. Click **"Next"**

### **2.3 Choose Location**
1. Select a **location** close to your users
2. Click **"Done"**

## 🔑 **Step 3: Create Service Accounts**

For each project:

### **3.1 Access Service Accounts**
1. In Firebase Console, click the **gear icon** (⚙️)
2. Select **"Project settings"**
3. Click **"Service accounts"** tab

### **3.2 Generate New Private Key**
1. Click **"Generate new private key"**
2. Click **"Generate key"**
3. **Download the JSON file**
4. **Save it securely** (don't commit to Git)

### **3.3 File Naming Convention**
Save the files as:
- `firebase_creds_testing.json`
- `firebase_creds_staging.json`
- `firebase_creds_production.json`

## 🔧 **Step 4: Set Up Railway Environment Variables**

### **4.1 Use the Setup Script**
```bash
python scripts/setup_firebase_projects.py
```

### **4.2 Manual Setup (Alternative)**

#### **For Testing**
```bash
railway service kickai-testing
railway variables --service kickai-testing --set FIREBASE_PROJECT_ID="kickai-testing"
railway variables --service kickai-testing --set FIREBASE_CREDENTIALS="$(cat firebase_creds_testing.json)"
```

#### **For Staging**
```bash
railway service kickai-staging
railway variables --service kickai-staging --set FIREBASE_PROJECT_ID="kickai-staging"
railway variables --service kickai-staging --set FIREBASE_CREDENTIALS="$(cat firebase_creds_staging.json)"
```

#### **For Production**
```bash
railway service kickai-production
railway variables --service kickai-production --set FIREBASE_PROJECT_ID="kickai-production"
railway variables --service kickai-production --set FIREBASE_CREDENTIALS="$(cat firebase_creds_production.json)"
```

## 📊 **Step 5: Set Up Firestore Collections**

For each project, create these collections:

### **5.1 Teams Collection**
```json
{
  "name": "Team Name",
  "description": "Team description",
  "is_active": true,
  "created_at": "timestamp",
  "settings": {
    "ai_provider": "google_gemini",
    "max_members": 100
  }
}
```

### **5.2 Team Bots Collection**
```json
{
  "team_id": "team-document-id",
  "bot_token": "BOT_TOKEN",
  "bot_username": "bot_username",
  "chat_id": "MAIN_CHAT_ID",
  "leadership_chat_id": "LEADERSHIP_CHAT_ID",
  "is_active": true,
  "created_at": "timestamp"
}
```

### **5.3 Team Members Collection**
```json
{
  "team_id": "team-document-id",
  "user_id": "telegram_user_id",
  "username": "telegram_username",
  "role": "admin|member|guest",
  "is_active": true,
  "joined_at": "timestamp"
}
```

## 🔒 **Step 6: Configure Security Rules**

### **6.1 Basic Security Rules**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to all users under any document
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### **6.2 Production Security Rules (Later)**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Teams collection
    match /teams/{teamId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Team bots collection
    match /team_bots/{botId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Team members collection
    match /team_members/{memberId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

## 🧪 **Step 7: Test the Setup**

### **7.1 Verify Environment Variables**
```bash
# Check testing
railway variables --service kickai-testing

# Check staging
railway variables --service kickai-staging

# Check production
railway variables --service kickai-production
```

### **7.2 Test Firebase Connection**
```bash
python test_bot_config.py
```

### **7.3 Deploy and Test**
```bash
# Deploy testing
railway service kickai-testing
railway up

# Deploy staging
railway service kickai-staging
railway up

# Deploy production
railway service kickai-production
railway up
```

## 📁 **File Structure After Setup**

```
KICKAI/
├── firebase_creds_testing.json     (testing credentials)
├── firebase_creds_staging.json     (staging credentials)
├── firebase_creds_production.json  (production credentials)
├── scripts/
│   └── setup_firebase_projects.py  (setup script)
└── config/
    ├── bot_config.json             (testing bot config)
    ├── bot_config.staging.json     (staging bot config)
    └── bot_config.production.json  (production bot config)
```

## 🔄 **Step 8: Update Bot Configuration**

### **8.1 Create Local Bot Configs**
```bash
# For testing
python scripts/setup_bot_config.py

# For staging
python scripts/setup_bot_config.py

# For production (will use Firestore)
# No local config needed
```

### **8.2 Set Bot Tokens**
```bash
# Testing bot token
railway variables --service kickai-testing --set TELEGRAM_BOT_TOKEN="your_testing_bot_token"

# Staging bot token
railway variables --service kickai-staging --set TELEGRAM_BOT_TOKEN="your_staging_bot_token"

# Production bot token
railway variables --service kickai-production --set TELEGRAM_BOT_TOKEN="your_production_bot_token"
```

## ✅ **Verification Checklist**

- [ ] **Firebase Projects Created**
  - [ ] `kickai-testing`
  - [ ] `kickai-staging`
  - [ ] `kickai-production`

- [ ] **Firestore Enabled**
  - [ ] Testing database
  - [ ] Staging database
  - [ ] Production database

- [ ] **Service Accounts Created**
  - [ ] Testing credentials downloaded
  - [ ] Staging credentials downloaded
  - [ ] Production credentials downloaded

- [ ] **Railway Variables Set**
  - [ ] Testing environment variables
  - [ ] Staging environment variables
  - [ ] Production environment variables

- [ ] **Collections Created**
  - [ ] Teams collection
  - [ ] Team bots collection
  - [ ] Team members collection

- [ ] **Security Rules Configured**
  - [ ] Basic rules for development
  - [ ] Production rules (when ready)

- [ ] **Bot Configuration**
  - [ ] Local configs for testing/staging
  - [ ] Firestore config for production

## 🚨 **Important Notes**

### **Security**
- **Never commit** Firebase credentials to Git
- **Use environment variables** for sensitive data
- **Rotate credentials** regularly
- **Monitor access** logs

### **Cost Management**
- **Free tier limits** apply per project
- **Monitor usage** in Firebase Console
- **Set up billing alerts** for production

### **Data Management**
- **Backup data** regularly
- **Test migrations** between environments
- **Document schema** changes

## 🆘 **Troubleshooting**

### **Common Issues**

1. **"Project not found"**
   - Check project ID spelling
   - Verify service account has access

2. **"Permission denied"**
   - Check service account permissions
   - Verify security rules

3. **"Invalid credentials"**
   - Regenerate service account key
   - Check JSON format

4. **"Collection not found"**
   - Create collections manually
   - Check collection names

### **Support Commands**
```bash
# Check Railway status
railway status

# View logs
railway logs --service kickai-testing

# Verify variables
railway variables --service kickai-testing

# Test connection
python test_bot_config.py
```

## 🎉 **Next Steps**

1. **Complete Firebase setup** using this guide
2. **Set up bot configurations** for each environment
3. **Deploy services** to Railway
4. **Test end-to-end** functionality
5. **Monitor and optimize** performance

This setup provides a robust, scalable foundation for your KICKAI system across all environments! 🚀 