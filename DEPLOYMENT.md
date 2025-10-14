# 🚀 SehatScan Deployment Guide

## 🌐 Streamlit Cloud Deployment

### **Quick Deploy to Streamlit Cloud:**

1. **Fork this repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"** and connect your GitHub account

4. **Select your forked repository**

5. **Configure the app:**
   - **Main file path**: `app.py`
   - **Python version**: 3.12 (recommended)

6. **Add your API keys** in Streamlit Cloud secrets:
   ```toml
   # In Streamlit Cloud > App Settings > Secrets
   HUGGINGFACE_API_KEY = "your_huggingface_api_key_here"
   GEMINI_API_KEY = "your_gemini_api_key_here"  # Optional
   ```

7. **Deploy!** Streamlit Cloud will automatically install dependencies from `requirements.txt`

### **Files for Streamlit Cloud:**
- ✅ `requirements.txt` - Python dependencies (OCR-free for compatibility)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `app.py` - Main application file (auto-detects OCR availability)

### **Streamlit Cloud Features:**
- ✅ **JSON Input** - Paste medical data directly
- ✅ **Data Visualization** - Interactive charts and gauges
- ✅ **AI Recommendations** - Full health suggestions
- ❌ **OCR Upload** - Not available (use JSON input instead)

## 🏠 Local Development

### **Using UV (Recommended):**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <your-repo>
cd SehatScan
uv sync --no-install-project

# Run locally
uv run streamlit run app.py
```

### **Using pip:**
```bash
# Clone and setup
git clone <your-repo>
cd SehatScan
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## 🔧 Configuration

### **Environment Variables:**
```bash
# Required
HUGGINGFACE_API_KEY=your_key_here

# Optional (for faster processing)
GEMINI_API_KEY=your_key_here
```

### **For Streamlit Cloud:**
Add these in **App Settings > Secrets** (not in code!)

### **For Local Development:**
Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your keys
```

## 🐛 Troubleshooting

### **Common Issues:**

1. **OCR Not Available on Streamlit Cloud:**
   - PaddleOCR is not compatible with Streamlit Cloud (Python 3.13 + system dependencies)
   - **This is expected behavior** - the app is designed to work without OCR
   - **Solution**: Use JSON input mode - all other features work perfectly
   - The app automatically detects this and shows appropriate interface

2. **API Keys:**
   - Make sure keys are properly set in Streamlit secrets
   - Check the sidebar for API key status

3. **Memory Issues:**
   - OCR processing can be memory-intensive
   - Consider using smaller images
   - Streamlit Cloud has memory limits

### **Performance Tips:**

1. **Use Python 3.12+** for best performance
2. **Add Gemini API key** for faster JSON processing
3. **Optimize images** before upload (clear, high contrast)
4. **Use caching** - identical reports return cached results

## 📊 Monitoring

### **Streamlit Cloud:**
- Check app logs in Streamlit Cloud dashboard
- Monitor resource usage
- Set up error notifications

### **Local Development:**
- Check terminal output for detailed logs
- Use browser developer tools for debugging
- Enable debug mode in Streamlit config

---

**Need help?** Check the logs or create an issue in the repository! 🆘