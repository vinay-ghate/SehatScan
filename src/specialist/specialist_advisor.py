"""
Specialist Advisor for generating AI-powered medical recommendations.

This module uses the exact working logic from specilistSuggest.py with optimizations for speed.
"""

import json
import logging
import hashlib
import os
from typing import Any, Optional
from huggingface_hub import InferenceClient
import google.generativeai as genai

# Python 3.12+ type aliases
type MedicalData = dict[str, Any]
type HealthRecommendations = dict[str, Any]

logger = logging.getLogger(__name__)


class SpecialistAdvisor:
    """
    An AI-powered advisor for generating medical recommendations.
    
    Uses the exact working logic from specilistSuggest.py with speed optimizations.
    """
    
    def __init__(self, api_key: str, gemini_api_key: Optional[str] = None):
        """
        Initialize the Specialist Advisor.
        
        Args:
            api_key (str): Hugging Face API key for medical model
            gemini_api_key (Optional[str]): Google Gemini API key for JSON formatting
        """
        self.api_key = api_key
        
        # Pre-initialize Hugging Face client for medical analysis
        self.medical_client = InferenceClient(
            provider="featherless-ai",
            api_key=api_key,
        )
        
        # Initialize Gemini for JSON formatting
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-image')
            logger.info("Gemini model initialized for JSON formatting")
        else:
            self.gemini_model = None
            logger.info("No Gemini key provided, will use Hugging Face fallback")
        
        # Note: Hugging Face formatter client is created fresh when needed (like original code)
        
        # Simple in-memory cache for speed
        self._cache = {}
        
        logger.info("Specialist Advisor initialized with optimized clients and caching")
    
    def get_health_recommendations(self, medical_data: MedicalData) -> HealthRecommendations:
        """
        Generate health recommendations using the exact logic from specilistSuggest.py.
        
        Args:
            medical_data (Dict[str, Any]): Structured medical data from OCR
            
        Returns:
            Dict[str, Any]: Structured health recommendations
        """
        try:
            # Convert medical data to JSON string (same as original)
            medical_json = json.dumps(medical_data, indent=2)
            
            # Check cache first for speed
            cache_key = hashlib.md5(medical_json.encode()).hexdigest()
            if cache_key in self._cache:
                logger.info("Returning cached health recommendations")
                return self._cache[cache_key]
            
            # Generate new recommendations
            result = self._get_health_plan_optimized(medical_json)
            
            # Cache successful results
            if "error" not in result:
                self._cache[cache_key] = result
                logger.info("Cached new health recommendations")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate health recommendations: {str(e)}")
            return {"error": f"Failed to generate recommendations: {str(e)}"}
    
    def _get_health_plan_optimized(self, medical_data: str) -> HealthRecommendations:
        """
        Optimized version of the original get_health_plan function.
        
        Args:
            medical_data (str): Medical data in JSON string format
            
        Returns:
            Dict[str, Any]: Structured health plan
        """
        # Step 1: Generate health plan text (same prompt as original)
        try:
            # Analyze findings for targeted prompt (optimization)
            findings = self._quick_analyze_findings(medical_data)
            findings_text = ", ".join(findings) if findings else "High WBC, High Creatinine, Low Potassium"
            
            prompt1 = f"""
            Analyze the following medical data. Based on the findings ({findings_text}),
            generate a detailed diet and exercise plan.

            **Medical Data:**
            ```json
            {medical_data}
            ```

            **Instructions:**
            1.  **Diet Plan:** Suggest specific foods to eat and avoid to address the {findings_text.lower()}.
            2.  **Exercise Plan:** Recommend safe and appropriate exercises (e.g., light cardio, strength training).
            3.  **Disclaimer:** Include a clear disclaimer that this is not a substitute for professional medical advice.
            4.  **Format:** Use clear headings for each section. Do not add any conversational intro or conclusion.
            """

            completion1 = self.medical_client.chat.completions.create(
                model="Intelligent-Internet/II-Medical-8B",
                messages=[{"role": "user", "content": prompt1}],
                max_tokens=1200,  # Reduced for speed
                temperature=0.5   # Reduced for faster, more focused responses
            )

            health_plan_text = completion1.choices[0].message.content

        except Exception as e:
            return {"error": f"Failed to get response from medical model: {e}"}

        # Step 2: Structure the output using Gemini or fallback
        try:
            return self._format_with_gemini_or_fallback(health_plan_text)

        except Exception as e:
            return {"error": f"Failed to format health plan: {e}"}
    
    def _format_with_gemini_or_fallback(self, health_plan_text: str) -> dict[str, Any]:
        """
        Format health plan using Gemini (preferred) or Hugging Face fallback.
        
        Args:
            health_plan_text (str): Raw health plan text
            
        Returns:
            Dict[str, Any]: Structured JSON response
        """
        prompt = f"""
        Convert the following health plan into a structured JSON object.
        Extract the information accurately and follow the specified format exactly.

        **Input Text:**
        ---
        {health_plan_text}
        ---

        **Required JSON Structure (copy this format exactly):**
        {{
          "diet_plan": {{
            "summary": "A brief, one-sentence summary of the dietary goals.",
            "foods_to_include": ["food1", "food2", "food3"],
            "foods_to_avoid": ["food1", "food2", "food3"]
          }},
          "exercise_plan": {{
            "summary": "A brief, one-sentence summary of the exercise goals.",
            "recommendations": [
              {{
                "activity": "Walking",
                "frequency": "Daily",
                "duration": "30 minutes per session"
              }},
              {{
                "activity": "Light strength training",
                "frequency": "2-3 times a week",
                "duration": "20-30 minutes per session"
              }}
            ]
          }},
          "disclaimer": "Information provided is for general use only and not for entire medical diagnosis. In serious conditions, consult a licensed healthcare professional."
        }}

        CRITICAL REQUIREMENTS:
        1. Output ONLY valid JSON - no markdown, no explanations, no extra text
        2. Use proper JSON array syntax with square brackets []
        3. Use proper JSON object syntax with curly braces {{}}
        4. All strings must be in double quotes
        5. No trailing commas
        6. Each recommendation must be a separate object in the array

        Your response:
        """
        
        # Try Gemini first (faster and more reliable for JSON)
        if self.gemini_model:
            try:
                logger.info("Using Gemini for JSON formatting")
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Very low for consistent JSON
                        max_output_tokens=1500,
                    )
                )
                
                json_output_str = response.text
                logger.info("Gemini formatting successful")
                
            except Exception as e:
                logger.warning(f"Gemini formatting failed: {e}, falling back to Hugging Face")
                return self._format_with_huggingface(prompt)
        else:
            # Use Hugging Face fallback
            return self._format_with_huggingface(prompt)
        
        # Clean and parse JSON output
        try:
            # Clean JSON output more thoroughly
            json_output_str = json_output_str.strip()
            
            # Remove markdown formatting
            if json_output_str.startswith("```json"):
                json_output_str = json_output_str[7:]
            elif json_output_str.startswith("```"):
                json_output_str = json_output_str[3:]
            
            if json_output_str.endswith("```"):
                json_output_str = json_output_str[:-3]
            
            json_output_str = json_output_str.strip()
            
            # Try to parse JSON
            final_json = json.loads(json_output_str)
            
            # Validate required structure
            if not self._validate_json_structure(final_json):
                logger.warning("JSON structure validation failed, trying fallback")
                return self._format_with_huggingface(prompt)
            
            logger.info("Successfully generated health recommendations with Gemini")
            return final_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON decode error: {str(e)}")
            logger.error(f"Raw output: {json_output_str[:200]}...")
            # Try Hugging Face fallback
            return self._format_with_huggingface(prompt)
    
    def _format_with_huggingface(self, prompt: str) -> dict[str, Any]:
        """
        Fallback formatting using Hugging Face DeepSeek model (exact logic from specilistSuggest.py).
        
        Args:
            prompt (str): Formatting prompt
            
        Returns:
            Dict[str, Any]: Structured JSON response
        """
        try:
            logger.info("Using Hugging Face DeepSeek for JSON formatting")
            
            # Create fresh client like in original code
            formatter_client = InferenceClient(
                provider="novita",
                api_key=self.api_key,
            )
            
            completion = formatter_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.2-Exp",
                messages=[{"role": "user", "content": prompt}],
            )

            json_output_str = completion.choices[0].message.content

            # Clean JSON output (exact same logic as original)
            if json_output_str.strip().startswith("```json"):
                json_output_str = json_output_str.strip()[7:-3]

            final_json = json.loads(json_output_str)
            logger.info("Successfully generated health recommendations with Hugging Face")
            return final_json

        except json.JSONDecodeError as e:
            logger.error(f"Hugging Face JSON decode error: {str(e)}")
            return {
                "error": "Failed to parse the final output into valid JSON.", 
                "raw_output": json_output_str if 'json_output_str' in locals() else "No output"
            }
        except Exception as e:
            logger.error(f"Hugging Face formatting error: {str(e)}")
            return {"error": f"Failed to get response from formatting model: {e}"}
    
    def _quick_analyze_findings(self, medical_data_str: str) -> list:
        """
        Quick analysis of medical findings for targeted prompts.
        
        Args:
            medical_data_str (str): Medical data JSON string
            
        Returns:
            list: List of key findings
        """
        findings = []
        
        try:
            medical_data = json.loads(medical_data_str)
            observations = medical_data.get('observations', [])
            
            for obs in observations:
                test_name = obs.get('test_name', '').lower()
                flag = obs.get('flag', 'N').upper()
                
                if flag == 'H':  # High values
                    if 'wbc' in test_name:
                        findings.append("High WBC")
                    elif 'creatinine' in test_name:
                        findings.append("High Creatinine")
                    elif 'glucose' in test_name:
                        findings.append("High Glucose")
                    elif 'cholesterol' in test_name:
                        findings.append("High Cholesterol")
                
                elif flag == 'L':  # Low values
                    if 'potassium' in test_name:
                        findings.append("Low Potassium")
                    elif 'hemoglobin' in test_name:
                        findings.append("Low Hemoglobin")
        
        except Exception as e:
            logger.debug(f"Quick analysis failed: {e}")
        
        return findings if findings else ["High WBC", "High Creatinine", "Low Potassium"] 
    def _validate_json_structure(self, data: dict[str, Any]) -> bool:
        """
        Validate that the JSON has the required structure.
        
        Args:
            data (Dict[str, Any]): Parsed JSON data
            
        Returns:
            bool: True if structure is valid
        """
        try:
            # Check required top-level keys
            required_keys = ['diet_plan', 'exercise_plan', 'disclaimer']
            for key in required_keys:
                if key not in data:
                    logger.error(f"Missing required key: {key}")
                    return False
            
            # Check diet_plan structure
            diet_plan = data['diet_plan']
            if not isinstance(diet_plan, dict):
                logger.error("diet_plan is not a dictionary")
                return False
            
            # Check exercise_plan structure
            exercise_plan = data['exercise_plan']
            if not isinstance(exercise_plan, dict):
                logger.error("exercise_plan is not a dictionary")
                return False
            
            # Check if recommendations is a list
            if 'recommendations' in exercise_plan:
                if not isinstance(exercise_plan['recommendations'], list):
                    logger.error("exercise_plan.recommendations is not a list")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"JSON validation error: {e}")
            return False