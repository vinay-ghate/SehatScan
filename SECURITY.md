# 🔐 Security Guidelines

## ⚠️ CRITICAL: API Key Security

### **NEVER commit real API keys to version control!**

## ✅ Security Checklist

### **Before Committing Code:**
- [ ] No hardcoded API keys in any `.py` files
- [ ] No real keys in `.env` file (use `.env.example` as template)
- [ ] All sensitive files are in `.gitignore`
- [ ] No database URLs or connection strings in code
- [ ] No passwords or tokens in comments

### **API Key Management:**
1. **Use Environment Variables:**
   ```python
   import os
   api_key = os.getenv('HUGGINGFACE_API_KEY')
   ```

2. **Local Development:**
   ```bash
   cp .env.example .env
   # Edit .env with your real keys (never commit this file)
   ```

3. **Production Deployment:**
   - Set environment variables in your hosting platform
   - Never include `.env` in production builds

### **Files That Should NEVER Contain Real Keys:**
- ❌ `specilistSuggest.py`
- ❌ `app.py` 
- ❌ Any `.py` file
- ❌ `README.md`
- ❌ `.env` (if committed to git)

### **Safe Files for Examples:**
- ✅ `.env.example` (with placeholder values)
- ✅ `README.md` (with placeholder examples)
- ✅ Documentation files

## 🛡️ What We've Secured

### **Removed from Code:**
- Hardcoded Hugging Face API key: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Hardcoded Gemini API key: `AIxxxxxxxxxxxxxxxxxxxxxxxx`

### **Security Measures Added:**
- Comprehensive `.gitignore` patterns
- Environment variable usage
- Security warnings in code comments
- This security documentation

## 🚨 If Keys Were Compromised

If any real API keys were committed to version control:

1. **Immediately revoke the keys** in the respective platforms:
   - [Hugging Face Tokens](https://huggingface.co/settings/tokens)
   - [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. **Generate new API keys**

3. **Update your local `.env` file** with new keys

4. **Never commit the new keys** to version control

## 📞 Security Contact

If you discover any security issues, please report them immediately.

---
**Remember: Security is everyone's responsibility! 🛡️**