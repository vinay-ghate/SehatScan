# 🩺 SehatScan

**AI-powered medical report analysis that makes your health data clear and accessible.**

SehatScan AI helps you instantly understand your lab reports in clear, simple language. It reads and explains key health markers, keeps your personal details private, and shares summaries in your preferred language. Behind the scenes, AI agents handle the complex work, but you just get clarity and peace of mind. It's not about replacing doctors, it's about making your health reports easy and accessible.

## ✨ What SehatScan Does

- **📄 Smart OCR**: Upload a photo of your medical report and get structured data instantly
- **📊 Visual Insights**: See your health markers in easy-to-understand charts and gauges
- **🤖 AI Recommendations**: Get personalized diet and exercise suggestions based on your results
- **🔒 Privacy First**: Your data stays on your device - nothing is stored or shared
- **🌐 Simple Interface**: Clean, intuitive design that anyone can use

## 🚀 Quick Start

### Prerequisites

- **Python 3.12 or higher** (recommended for optimal performance and latest features)
- UV package manager (modern Python package management)

### Installation

1. **Get the code:**
   ```bash
   git clone https://github.com/vinay-ghate/SehatScan
   cd SehatScan
   ```

2. **Install UV package manager:**
   ```bash
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies:**
   
   **Option A: Using UV (Recommended for local development):**
   ```bash
   uv sync --no-install-project
   ```
   
   **Option B: Using pip:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API keys:**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys (see setup guide below)
   ```

5. **Run SehatScan:**
   
   **With UV:**
   ```bash
   uv run streamlit run app.py
   ```
   
   **With pip:**
   ```bash
   streamlit run app.py
   ```

## 🔑 API Setup

SehatScan needs AI services to analyze your reports:

1. **Hugging Face** (Required):
   - Go to [huggingface.co](https://huggingface.co)
   - Sign up and create an API token
   - Add it to your `.env` file

2. **Google Gemini** (Optional - for faster processing):
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add it to your `.env` file

## 🎯 How to Use

### Upload Your Report
1. Take a clear photo of your medical report
2. Upload it in the "Upload Image" tab
3. Click "Process Document"

### Get Instant Analysis
- **Extracted Data**: See your test results in a clean table
- **Visual Charts**: Understand your levels with color-coded gauges
- **AI Insights**: Get personalized health recommendations

### Alternative: Paste JSON Data
If you already have digital medical data, paste it in the "Input JSON" tab.

> **Note**: On some cloud platforms (like Streamlit Cloud), OCR may not be available due to system dependencies. The app will automatically show the JSON input option as the primary method.

## 🛡️ Privacy & Security

- **Local Processing**: Your medical data never leaves your device
- **No Storage**: Reports are not saved or stored anywhere
- **Secure**: API keys are kept private in your local environment
- **Open Source**: Full transparency - you can see exactly what the code does

## 📱 Supported Formats

- **Images**: PNG, JPG, JPEG medical reports
- **Languages**: English (more coming soon)
- **Report Types**: Blood tests, lab results, diagnostic reports

## ⚠️ Important Disclaimer

SehatScan is designed to help you understand your medical reports better. It is **not a substitute for professional medical advice**. Always consult with your healthcare provider for medical decisions and treatment plans.

## 🛠️ For Developers

### Project Structure
```
SehatScan/
├── src/
│   ├── medical_ocr/     # OCR processing
│   ├── visualizer/      # Data visualization
│   └── specialist/      # AI recommendations
├── app.py              # Main application
└── pyproject.toml      # Dependencies
```

### Tech Stack
- **Frontend**: Streamlit
- **OCR**: PaddleOCR
- **Visualization**: Plotly
- **AI**: Hugging Face + Google Gemini
- **Package Management**: UV

## 🤝 Contributing

We welcome contributions! Whether it's bug fixes, new features, or documentation improvements.

## 📄 License

MIT License - feel free to use and modify.

---

**Made with ❤️ for better health understanding**
