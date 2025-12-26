"""Gemini synthesis of LLM recommendations"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiSynthesizer:
    """Synthesize recommendations from multiple LLMs using Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.enabled = GEMINI_AVAILABLE and bool(self.api_key)
        
        if self.enabled:
            genai.configure(api_key=self.api_key)
            logger.info("✅ Gemini synthesizer enabled")
        else:
            logger.warning("Gemini not enabled - set GOOGLE_API_KEY")
    
    def synthesize(self, llm_recommendations: Dict[str, Optional[str]]) -> Optional[str]:
        """
        Synthesize recommendations from multiple LLMs using Gemini
        
        Args:
            llm_recommendations: Dictionary with LLM names and their recommendations
            
        Returns:
            Final synthesized recommendations
        """
        if not self.enabled:
            logger.warning("Gemini not enabled")
            return None
        
        # Filter out None values
        valid_recommendations = {
            name: rec for name, rec in llm_recommendations.items() if rec
        }
        
        if not valid_recommendations:
            logger.warning("No valid LLM recommendations to synthesize")
            return None
        
        try:
            # Build prompt with all recommendations
            recommendations_text = ""
            for name, rec in valid_recommendations.items():
                recommendations_text += f"\n\n=== {name.upper()} RECOMMENDATIONS ===\n{rec}\n"
            
            prompt = f"""You are an expert forex trader with over 20 years of experience reviewing recommendations from multiple AI analysts. Each analyst has provided recommendations based on BOTH:
1. Data from the Google Drive "Forex tracker" folder (hourly reports on trending currencies)
2. Their own research of current news, market trends, and currency movements

Review the following recommendations from ChatGPT, Gemini, and Claude. Analyze them, identify convergence points, and provide your final trading recommendations.

{recommendations_text}

Based on your review of all recommendations:
1. Identify the strongest trading opportunities (where multiple analysts agree)
2. Consider upcoming high-impact news events that might cause sudden reversals
3. Cross-reference findings from Google Drive data with current market research
4. Provide final trading recommendations with specific:
   - Currency pairs
   - Entry prices (exact levels)
   - Exit/target prices (exact levels)
   - Stop loss levels (exact levels)
   - Position sizing guidance
   - Rationale for each recommendation (synthesizing insights from both data sources)
   - Risk assessment including news event impact

Format your recommendations clearly with specific price levels that can be used for automated monitoring and alerts. Ensure all price levels are exact and actionable.
"""
            
            gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            # Try primary model first, with fallbacks
            try:
                model = genai.GenerativeModel(gemini_model)
            except Exception as model_error:
                logger.warning(f"Model {gemini_model} failed, trying gemini-1.5-pro: {model_error}")
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    gemini_model = 'gemini-1.5-pro'
                except Exception:
                    logger.warning("gemini-1.5-pro failed, trying gemini-pro")
                    model = genai.GenerativeModel('gemini-pro')
                    gemini_model = 'gemini-pro'
            
            response = model.generate_content(prompt)
            result = response.text
            logger.info(f"✅ Gemini synthesis completed (model: {gemini_model})")
            return result
            
        except Exception as e:
            logger.error(f"Error with Gemini synthesis: {e}")
            return None

