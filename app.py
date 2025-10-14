"""
SehatScan - AI-Powered Medical Report Analysis

SehatScan helps you understand your lab reports in clear, simple language.
It reads and explains key health markers while keeping your data private.

Features:
- Smart OCR processing of medical documents
- Interactive data visualization
- AI-powered health recommendations

Version: 0.1.0
"""

import streamlit as st
import json
import logging
import os
import sys
from typing import Any, Optional
from PIL import Image
import io

# Python 3.12+ type aliases for better code readability
type MedicalData = dict[str, Any]

# Check Python version
if sys.version_info < (3, 12):
    st.warning(
        f"⚠️ You're using Python {sys.version_info.major}.{sys.version_info.minor}. "
        f"SehatScan is optimized for Python 3.12+ for better performance and features."
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules with error handling
try:
    from src.medical_ocr import MedicalOCRProcessor
    OCR_IMPORT_SUCCESS = True
except Exception as e:
    logger.warning(f"OCR module import failed: {e}")
    MedicalOCRProcessor = None
    OCR_IMPORT_SUCCESS = False

from src.visualizer import MedicalDataVisualizer
from src.specialist import SpecialistAdvisor

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class SehatScanApp:
    """Main application class for SehatScan."""
    
    def __init__(self):
        """Initialize the application components."""
        self.ocr_processor = None
        self.visualizer = MedicalDataVisualizer()
        self.specialist_advisor = None
        
    def initialize_ocr(self):
        """Initialize OCR processor (lazy loading for performance)."""
        if self.ocr_processor is None:
            if not OCR_IMPORT_SUCCESS or MedicalOCRProcessor is None:
                st.error("❌ OCR functionality not available")
                st.info(
                    "🔄 **Alternative Options:**\n"
                    "- Use the 'Input JSON' tab to paste medical data directly\n"
                    "- OCR dependencies may not be available on this platform\n"
                    "- For local development, install with: `uv sync --extra ocr`"
                )
                return None
            
            with st.spinner("Initializing OCR processor..."):
                try:
                    self.ocr_processor = MedicalOCRProcessor()
                except Exception as e:
                    st.error(f"❌ OCR initialization failed: {str(e)}")
                    st.info("💡 You can still use the JSON input feature!")
                    return None
        return self.ocr_processor
    
    def initialize_specialist_advisor(self, api_key: str):
        """Initialize specialist advisor with API key."""
        if self.specialist_advisor is None:
            # Get Gemini API key from environment
            gemini_key = os.getenv("GEMINI_API_KEY")
            
            # Need at least one API key to work
            if api_key or gemini_key:
                try:
                    self.specialist_advisor = SpecialistAdvisor(api_key, gemini_key)
                    logger.info("Specialist advisor initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize specialist advisor: {e}")
                    self.specialist_advisor = None
            else:
                logger.warning("No API keys provided for specialist advisor")
                self.specialist_advisor = None
        
        return self.specialist_advisor


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="SehatScan",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton > button {
        background: #3b82f6;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background: #2563eb;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the application sidebar."""
    st.sidebar.title("🩺 SehatScan")
    st.sidebar.markdown("---")
    
    # Check for environment variables first
    default_hf_key = os.getenv("HUGGINGFACE_API_KEY", "")
    default_gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    api_key = st.sidebar.text_input(
        "Hugging Face API Key",
        value=default_hf_key,
        type="password",
        help="For medical analysis. Can be omitted if Gemini key is provided."
    )
    
    gemini_key = st.sidebar.text_input(
        "Gemini API Key",
        value=default_gemini_key,
        type="password",
        help="Can handle both medical analysis and formatting. Faster than Hugging Face."
    )
    
    # Set Gemini key in environment for the specialist advisor
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    
    # Show API key status
    if not api_key and not gemini_key:
        st.sidebar.error("❌ No API keys provided - specialist recommendations unavailable")
    elif not api_key and gemini_key:
        st.sidebar.success("✅ Gemini-only mode enabled (handles both medical analysis and formatting)")
    elif api_key and not gemini_key:
        st.sidebar.info("ℹ️ Hugging Face mode (medical analysis + formatting)")
    elif api_key and gemini_key:
        st.sidebar.success("✅ Optimal setup: Hugging Face + Gemini (fastest processing)")
    
    st.sidebar.markdown("---")
    
    # Application Info
    st.sidebar.subheader("ℹ️ About")
    # Check OCR availability for sidebar info
    if OCR_IMPORT_SUCCESS:
        try:
            from src.medical_ocr.ocr_processor import PADDLEOCR_AVAILABLE
            if PADDLEOCR_AVAILABLE:
                ocr_status = "📄 **Smart OCR** - Reads your report images"
            else:
                ocr_status = "📝 **JSON Input** - Paste your medical data directly"
        except:
            ocr_status = "📝 **JSON Input** - Paste your medical data directly"
    else:
        ocr_status = "📝 **JSON Input** - Paste your medical data directly"
    
    st.sidebar.info(
        f"SehatScan makes your medical reports easy to understand:\n\n"
        f"{ocr_status}\n"
        f"📊 **Visual Charts** - Shows your health data clearly\n"
        f"🤖 **AI Insights** - Provides personalized recommendations\n\n"
        f"🔒 **Privacy First** - Your data stays on your device"
    )
    
    return api_key


def render_file_upload():
    """Render file upload section."""
    st.subheader("📄 Upload Medical Document")
    
    uploaded_file = st.file_uploader(
        "Choose your medical report image",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Upload a clear image of your medical report"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        if uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Medical Report", use_container_width=True)
            return image
        else:
            st.error("PDF processing not yet implemented. Please upload an image file.")
            return None
    
    return None


def render_json_input():
    """Render JSON input section."""
    st.subheader("📝 Or Input JSON Data Directly")
    
    json_input = st.text_area(
        "Paste your medical data in JSON format",
        height=200,
        placeholder='{\n  "patient": {...},\n  "observations": [...]\n}'
    )
    
    if json_input:
        try:
            data = json.loads(json_input)
            st.success("✅ Valid JSON format")
            return data
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {str(e)}")
    
    return None


def process_medical_document(app: SehatScanApp, image: Image.Image) -> Optional[MedicalData]:
    """Process medical document using OCR."""
    try:
        with st.spinner("🔍 Processing medical document with OCR..."):
            ocr_processor = app.initialize_ocr()
            
            # Convert PIL image to format suitable for OCR
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Process with OCR
            medical_data = ocr_processor.process_image(img_byte_arr)
            
            st.success("✅ OCR processing completed successfully!")
            return medical_data
            
    except Exception as e:
        st.error(f"❌ OCR processing failed: {str(e)}")
        logger.error(f"OCR processing error: {str(e)}")
        return None


def display_extracted_data(medical_data: MedicalData):
    """Display extracted medical data."""
    st.subheader("📊 Extracted Medical Data")
    
    # Patient Information
    if 'patient' in medical_data and medical_data['patient']:
        st.write("**Patient Information:**")
        patient_info = medical_data['patient']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'name' in patient_info:
                st.write(f"Name: {patient_info['name']}")
        with col2:
            if 'dob' in patient_info:
                st.write(f"DOB: {patient_info['dob']}")
        with col3:
            if 'sex' in patient_info:
                st.write(f"Sex: {patient_info['sex']}")
    
    # Report Details
    if 'report_details' in medical_data and medical_data['report_details']:
        st.write("**Report Details:**")
        report_details = medical_data['report_details']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'report_date' in report_details:
                st.write(f"Date: {report_details['report_date']}")
        with col2:
            if 'specimen' in report_details:
                st.write(f"Specimen: {report_details['specimen']}")
        with col3:
            if 'accession' in report_details:
                st.write(f"Accession: {report_details['accession']}")
    
    # Test Results
    if 'observations' in medical_data and medical_data['observations']:
        st.write("**Test Results:**")
        observations_df = st.dataframe(medical_data['observations'], use_container_width=True)
    
    # Raw JSON (expandable)
    with st.expander("🔍 View Raw JSON Data"):
        st.json(medical_data)


def create_visualizations(app: SehatScanApp, medical_data: MedicalData):
    """Create and display visualizations."""
    st.subheader("📈 Data Visualizations")
    
    try:
        with st.spinner("🎨 Creating visualizations..."):
            visualizations = app.visualizer.create_visualizations(medical_data)
        
        if not visualizations:
            st.warning("⚠️ No visualizations could be created from the data")
            return
        
        st.success(f"✅ Created {len(visualizations)} visualizations")
        
        # Group visualizations by type
        gauge_charts = {k: v for k, v in visualizations.items() if 'gauge' in k}
        overview_charts = {k: v for k, v in visualizations.items() if 'gauge' not in k}
        
        # Display gauge charts
        if gauge_charts:
            st.write("**Individual Test Results:**")
            
            # Display gauge charts in columns
            num_gauges = len(gauge_charts)
            cols_per_row = 3
            
            gauge_items = list(gauge_charts.items())
            for i in range(0, num_gauges, cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < num_gauges:
                        name, fig = gauge_items[i + j]
                        with col:
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Display overview charts
        if overview_charts:
            st.write("**Overview Charts:**")
            for name, fig in overview_charts.items():
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    except Exception as e:
        st.error(f"❌ Failed to create visualizations: {str(e)}")
        logger.error(f"Visualization error: {str(e)}")


def generate_recommendations(app: SehatScanApp, medical_data: MedicalData, api_key: str):
    """Generate AI-powered specialist recommendations."""
    st.subheader("🩺 Specialist Recommendations")
    
    if not api_key and not os.getenv("GEMINI_API_KEY"):
        st.warning("⚠️ Please provide at least one API key (Hugging Face or Gemini) to generate recommendations")
        st.info(
            "**API Key Options:**\n"
            "- **Hugging Face**: For medical analysis (required if no Gemini)\n"
            "- **Gemini**: Can handle both medical analysis and formatting\n"
            "- **Both**: Optimal setup for fastest processing"
        )
        return
    
    try:
        # Show progress steps for better UX
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔧 Initializing AI models...")
        progress_bar.progress(20)
        specialist_advisor = app.initialize_specialist_advisor(api_key)
        
        if specialist_advisor is None:
            progress_bar.empty()
            status_text.empty()
            st.error("❌ Failed to initialize AI services")
            st.info(
                "**Please check:**\n"
                "- At least one API key is provided (Hugging Face or Gemini)\n"
                "- API keys are valid and have proper permissions\n"
                "- Network connection is available"
            )
            return
        
        status_text.text("🧠 Analyzing medical data...")
        progress_bar.progress(40)
        
        status_text.text("💊 Generating diet recommendations...")
        progress_bar.progress(60)
        
        status_text.text("🏃‍♂️ Creating exercise plan...")
        progress_bar.progress(80)
        
        recommendations = specialist_advisor.get_health_recommendations(medical_data)
        
        status_text.text("✅ Recommendations ready!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in recommendations:
            st.error(f"❌ Failed to generate recommendations: {recommendations['error']}")
            return
        
        st.success("✅ Recommendations generated successfully!")
        
        # Display Diet Plan
        if 'diet_plan' in recommendations:
            st.write("### 🥗 Diet Plan")
            diet_plan = recommendations['diet_plan']
            
            if 'summary' in diet_plan:
                st.write(f"**Summary:** {diet_plan['summary']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'foods_to_include' in diet_plan:
                    st.write("**Foods to Include:**")
                    for food in diet_plan['foods_to_include']:
                        st.write(f"• {food}")
            
            with col2:
                if 'foods_to_avoid' in diet_plan:
                    st.write("**Foods to Avoid:**")
                    for food in diet_plan['foods_to_avoid']:
                        st.write(f"• {food}")
            
            if 'meal_suggestions' in diet_plan:
                st.write("**Meal Suggestions:**")
                for suggestion in diet_plan['meal_suggestions']:
                    st.write(f"• {suggestion}")
        
        # Display Exercise Plan
        if 'exercise_plan' in recommendations:
            st.write("### 🏃‍♂️ Exercise Plan")
            exercise_plan = recommendations['exercise_plan']
            
            if 'summary' in exercise_plan:
                st.write(f"**Summary:** {exercise_plan['summary']}")
            
            # Handle both simple and complex exercise plan formats
            if 'recommendations' in exercise_plan:
                # Simple format with recommendations array (from original specilistSuggest.py)
                st.write("**Exercise Recommendations:**")
                recommendations_list = exercise_plan['recommendations']
                
                if isinstance(recommendations_list, list):
                    for i, rec in enumerate(recommendations_list):
                        if isinstance(rec, dict):
                            activity = rec.get('activity', f'Activity {i+1}')
                            frequency = rec.get('frequency', 'Not specified')
                            duration = rec.get('duration', 'Not specified')
                            
                            st.write(f"**{activity}**")
                            st.write(f"  • Frequency: {frequency}")
                            st.write(f"  • Duration: {duration}")
                            st.write("")
                        else:
                            st.write(f"• {rec}")
                else:
                    st.write("• Exercise recommendations format error")
            
            else:
                # Complex format with separate cardiovascular and strength training
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'cardiovascular' in exercise_plan:
                        cardio = exercise_plan['cardiovascular']
                        st.write("**Cardiovascular Exercise:**")
                        if 'activities' in cardio:
                            for activity in cardio['activities']:
                                st.write(f"• {activity}")
                        if 'frequency' in cardio:
                            st.write(f"**Frequency:** {cardio['frequency']}")
                        if 'duration' in cardio:
                            st.write(f"**Duration:** {cardio['duration']}")
                
                with col2:
                    if 'strength_training' in exercise_plan:
                        strength = exercise_plan['strength_training']
                        st.write("**Strength Training:**")
                        if 'activities' in strength:
                            for activity in strength['activities']:
                                st.write(f"• {activity}")
                        if 'frequency' in strength:
                            st.write(f"**Frequency:** {strength['frequency']}")
                        if 'duration' in strength:
                            st.write(f"**Duration:** {strength['duration']}")
                
                if 'additional_recommendations' in exercise_plan:
                    st.write("**Additional Recommendations:**")
                    for rec in exercise_plan['additional_recommendations']:
                        st.write(f"• {rec}")
        
        # Display General Recommendations
        if 'general_recommendations' in recommendations:
            st.write("### 📋 General Recommendations")
            general = recommendations['general_recommendations']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'lifestyle_changes' in general:
                    st.write("**Lifestyle Changes:**")
                    for change in general['lifestyle_changes']:
                        st.write(f"• {change}")
            
            with col2:
                if 'monitoring' in general:
                    st.write("**Monitoring:**")
                    for item in general['monitoring']:
                        st.write(f"• {item}")
            
            with col3:
                if 'follow_up' in general:
                    st.write("**Follow-up:**")
                    for item in general['follow_up']:
                        st.write(f"• {item}")
        
        # Display Disclaimer
        if 'disclaimer' in recommendations:
            st.warning(f"**⚠️ Disclaimer:** {recommendations['disclaimer']}")
        
        # Raw recommendations (expandable)
        with st.expander("🔍 View Raw Recommendations JSON"):
            st.json(recommendations)
            
        # Debug info if there are issues
        if 'error' in recommendations:
            st.error("❌ There was an issue generating recommendations")
            if 'raw_output' in recommendations:
                with st.expander("🐛 Debug: Raw AI Output"):
                    st.text(recommendations['raw_output'])
    
    except Exception as e:
        st.error(f"❌ Failed to generate recommendations: {str(e)}")
        logger.error(f"Recommendation generation error: {str(e)}")


def main():
    """Main application function."""
    configure_page()
    
    # Initialize application
    app = SehatScanApp()
    
    # Render sidebar and get API key
    api_key = render_sidebar()
    
    # Main content
    st.title("🩺 SehatScan")
    st.markdown("**AI-powered medical report analysis that makes your health data clear and accessible.**")
    
    # Check if running on Streamlit Cloud (OCR not available)
    if OCR_IMPORT_SUCCESS:
        try:
            from src.medical_ocr.ocr_processor import PADDLEOCR_AVAILABLE
            if not PADDLEOCR_AVAILABLE:
                st.info(
                    "ℹ️ **Running in Cloud Mode**: OCR is not available on this platform. "
                    "Please use the **'Input JSON'** tab to paste your medical data directly. "
                    "All visualization and AI recommendation features are fully available!"
                )
        except:
            st.info(
                "ℹ️ **JSON Input Mode**: Use the **'Input JSON'** tab to paste your medical data. "
                "All visualization and AI recommendation features are available!"
            )
    else:
        st.info(
            "ℹ️ **JSON Input Mode**: Use the **'Input JSON'** tab to paste your medical data. "
            "All visualization and AI recommendation features are available!"
        )
    
    st.markdown("Get instant insights, visual charts, and personalized health recommendations from your medical data.")
    
    # Create tabs for different input methods
    # Check OCR availability to determine tab order and labels
    if OCR_IMPORT_SUCCESS:
        try:
            from src.medical_ocr.ocr_processor import PADDLEOCR_AVAILABLE
            if PADDLEOCR_AVAILABLE:
                tab1, tab2 = st.tabs(["📄 Upload Image", "📝 Input JSON"])
            else:
                tab1, tab2 = st.tabs(["📝 Input JSON Data", "📄 Upload Image (Not Available)"])
        except:
            tab1, tab2 = st.tabs(["📝 Input JSON Data", "📄 Upload Image (Not Available)"])
    else:
        tab1, tab2 = st.tabs(["📝 Input JSON Data", "📄 Upload Image (Not Available)"])
    
    medical_data = None
    
    # Handle tab content based on OCR availability
    if OCR_IMPORT_SUCCESS:
        try:
            from src.medical_ocr.ocr_processor import PADDLEOCR_AVAILABLE
            ocr_available = PADDLEOCR_AVAILABLE
        except:
            ocr_available = False
    else:
        ocr_available = False
    
    if ocr_available:
        # OCR is available - normal flow
        with tab1:
            uploaded_image = render_file_upload()
            if uploaded_image is not None:
                if st.button("🔍 Process Document", key="process_ocr"):
                    ocr_processor = app.initialize_ocr()
                    if ocr_processor is not None:
                        medical_data = process_medical_document(app, uploaded_image)
                    else:
                        st.error("❌ Cannot process document: OCR not available")
        
        with tab2:
            json_data = render_json_input()
            if json_data is not None:
                medical_data = json_data
    else:
        # OCR not available - JSON first, disabled image upload
        with tab1:
            json_data = render_json_input()
            if json_data is not None:
                medical_data = json_data
        
        with tab2:
            st.warning("📄 **Image Upload Not Available**")
            st.info(
                "OCR functionality is not available on this platform. "
                "This is common on cloud deployments due to system dependencies.\n\n"
                "**Alternative**: Use the 'Input JSON Data' tab to paste your medical data directly."
            )
            st.markdown("**Sample JSON format:**")
            st.code('''
{
  "patient": {"name": "John Doe", "dob": "01/01/1990", "sex": "Male"},
  "observations": [
    {"test_name": "Hemoglobin", "result": "13.5", "unit": "g/dL", "reference_range": "12.0-16.0", "flag": "N"},
    {"test_name": "Glucose", "result": "95", "unit": "mg/dL", "reference_range": "70-99", "flag": "N"}
  ]
}
            ''', language="json")

    
    # Process and display results if we have medical data
    if medical_data is not None:
        st.markdown("---")
        
        # Display extracted data
        display_extracted_data(medical_data)
        
        st.markdown("---")
        
        # Create visualizations
        create_visualizations(app, medical_data)
        
        st.markdown("---")
        
        # Generate recommendations
        generate_recommendations(app, medical_data, api_key)


if __name__ == "__main__":
    main()