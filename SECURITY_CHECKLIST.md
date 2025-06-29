# Security Checklist

## 🚨 **CRITICAL: Never Commit Secrets to GitHub**

### **What NOT to commit:**
- ❌ Firebase service account keys
- ❌ API keys (Google, OpenAI, etc.)
- ❌ Database passwords
- ❌ Private keys
- ❌ Access tokens
- ❌ Environment files with real values

### **What IS safe to commit:**
- ✅ Placeholder values (e.g., `your-api-key-here`)
- ✅ Example configurations
- ✅ Documentation with dummy values
- ✅ Code that reads from environment variables

---

## 🔒 **Security Best Practices**

### **1. Environment Variables**
- Store all secrets in environment variables
- Use `.env` files locally (in .gitignore)
- Use Railway/Heroku environment variables in production
- Never hardcode secrets in code

### **2. Configuration Files**
- Keep `firebase_settings.json` in .gitignore
- Use placeholder values in documentation
- Create `env.example` with dummy values

### **3. Before Committing**
- ✅ Check for hardcoded secrets
- ✅ Verify .gitignore includes sensitive files
- ✅ Review all changed files
- ✅ Use `git diff` to see what's being committed

---

## 📋 **Pre-commit Checklist**

Before every commit, verify:

- [ ] No API keys in code
- [ ] No database credentials
- [ ] No private keys
- [ ] No real project IDs
- [ ] No actual email addresses
- [ ] Documentation uses placeholders

---

## 🛠️ **Tools to Help**

### **Check for secrets:**
```bash
# Search for common secret patterns
grep -r "sk-" . --exclude-dir=venv --exclude-dir=.git
grep -r "AIza" . --exclude-dir=venv --exclude-dir=.git
grep -r "-----BEGIN PRIVATE KEY-----" . --exclude-dir=venv --exclude-dir=.git
```

### **Verify .gitignore:**
```bash
# Check if files are ignored
git check-ignore .env
git check-ignore firebase_settings.json
```

---

## 🚨 **If Secrets Are Exposed**

1. **IMMEDIATELY** revoke the exposed credentials
2. Remove from git history if possible
3. Generate new credentials
4. Update all environments
5. Document the incident

---

## ✅ **Current Status**

- ✅ `.env` in .gitignore
- ✅ `firebase_settings.json` in .gitignore
- ✅ README uses placeholders
- ✅ No secrets in git history
- ✅ Environment variables used in production

**Last Updated:** December 19, 2024 