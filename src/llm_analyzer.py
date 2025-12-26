"""LLM analysis: ChatGPT, Gemini, Claude"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

# Gemini - Use the working package (google-generativeai)
# Note: google-genai has different API, stick with google-generativeai for now
try:
    # Explicitly import generativeai to avoid conflict with google-genai
    from google import generativeai
    genai = generativeai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to direct import
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False

# Claude
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ChatGPT
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class LLMAnalyzer:
    """Analyze forex data using multiple LLMs"""
    
    def __init__(self):
        """Initialize LLM analyzers"""
        # ChatGPT
        self.chatgpt_api_key = os.getenv('OPENAI_API_KEY')
        self.chatgpt_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.chatgpt_enabled = OPENAI_AVAILABLE and bool(self.chatgpt_api_key)
        if self.chatgpt_enabled:
            self.chatgpt_client = OpenAI(api_key=self.chatgpt_api_key)
            logger.info(f"✅ ChatGPT enabled (model: {self.chatgpt_model})")
        
        # Gemini
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        self.gemini_enabled = GEMINI_AVAILABLE and bool(self.gemini_api_key)
        if self.gemini_enabled:
            genai.configure(api_key=self.gemini_api_key)
            logger.info("✅ Gemini enabled")
        
        # Claude
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.claude_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        self.claude_enabled = ANTHROPIC_AVAILABLE and bool(self.claude_api_key)
        if self.claude_enabled:
            self.claude_client = Anthropic(api_key=self.claude_api_key)
            logger.info("✅ Claude enabled")
        
    
    def _get_chatgpt_prompt(self, data_summary: str) -> str:
        """Get prompt for ChatGPT"""
        return f"""As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

1. INFORMATION FROM GOOGLE DRIVE (Forex tracker folder):
The following data contains hourly reports on trending currencies retrieved from the Google Drive folder called "Forex tracker":
{data_summary}

2. YOUR OWN RESEARCH:
You have access to current forex market information, global events, news, and real-time currency trends. Use your knowledge and research capabilities to:
- Research current market trends and currency movements
- Identify relevant news events and economic indicators
- Analyze technical and fundamental factors
- Fact-check and validate information from the Google Drive data
- Identify any discrepancies or additional opportunities not in the provided data

ANALYSIS REQUIREMENTS:
Based on BOTH the Google Drive information AND your own research of current news and currency trends, provide your recommendations regarding any available trading opportunities currently in the market. Also provide updated risk-managed entry/exit price levels and position sizing guidance based on current price action. As part of the analysis, check if there are any upcoming high-impact news events today that might cause a sudden reversal in this trend.

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices (exact levels)
- Exit/target prices (exact levels)
- Stop loss levels (exact levels)
- Position sizing recommendations
- Rationale for each recommendation (indicating which insights came from Google Drive data vs. your own research)
- Upcoming high-impact news events that might affect the trend
"""

    def _get_gemini_prompt(self, data_summary: str) -> str:
        """Get prompt for Gemini"""
        return f"""As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

1. INFORMATION FROM GOOGLE DRIVE (Forex tracker folder):
The following data contains hourly reports on trending currencies retrieved from the Google Drive folder called "Forex tracker":
{data_summary}

2. YOUR OWN RESEARCH:
You have access to current forex market information, global events, news, and real-time currency trends. Use your knowledge and research capabilities to:
- Research current market trends and currency movements
- Identify relevant news events and economic indicators
- Analyze technical and fundamental factors
- Fact-check and validate information from the Google Drive data
- Identify any discrepancies or additional opportunities not in the provided data

ANALYSIS REQUIREMENTS:
Based on BOTH the Google Drive information AND your own research of current news and currency trends, provide your recommendations regarding any available trading opportunities currently in the market. Also provide updated risk-managed entry/exit price levels and position sizing guidance based on current price action. As part of the analysis, check if there are any upcoming high-impact news events today that might cause a sudden reversal in this trend.

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices (exact levels)
- Exit/target prices (exact levels)
- Stop loss levels (exact levels)
- Position sizing recommendations
- Rationale for each recommendation (indicating which insights came from Google Drive data vs. your own research)
- Upcoming high-impact news events that might affect the trend
"""

    def _get_claude_prompt(self, data_summary: str) -> str:
        """Get prompt for Claude"""
        return f"""As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

1. INFORMATION FROM GOOGLE DRIVE (Forex tracker folder):
The following data contains hourly reports on trending currencies retrieved from the Google Drive folder called "Forex tracker":
{data_summary}

2. YOUR OWN RESEARCH:
You have access to current forex market information, global events, news, and real-time currency trends. Use your knowledge and research capabilities to:
- Research current market trends and currency movements
- Identify relevant news events and economic indicators
- Analyze technical and fundamental factors
- Fact-check and validate information from the Google Drive data
- Identify any discrepancies or additional opportunities not in the provided data

ANALYSIS REQUIREMENTS:
Based on BOTH the Google Drive information AND your own research of current news and currency trends, provide your recommendations regarding any available trading opportunities currently in the market. Also provide updated risk-managed entry/exit price levels and position sizing guidance based on current price action. As part of the analysis, check if there are any upcoming high-impact news events today that might cause a sudden reversal in this trend.

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices (exact levels)
- Exit/target prices (exact levels)
- Stop loss levels (exact levels)
- Position sizing recommendations
- Rationale for each recommendation (indicating which insights came from Google Drive data vs. your own research)
- Upcoming high-impact news events that might affect the trend
"""

    def analyze_with_gemini(self, data_summary: str) -> Optional[str]:
        """Analyze using Gemini"""
        if not self.gemini_enabled:
            logger.warning("Gemini not enabled")
            return None
        
        try:
            # First, try to list available models to find what works
            gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            
            # Get available models and use them
            available_model_names = []
            try:
                available_models = genai.list_models()
                available_model_names = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
                logger.info(f"Available Gemini models: {len(available_model_names)} found")
                if available_model_names:
                    logger.info(f"First 5: {available_model_names[:5]}")
            except Exception as e:
                logger.warning(f"Could not list models: {e}")
            
            # Try available models first, then fallback to common names
            models_to_try = []
            
            # Add available models first (they're most likely to work)
            if available_model_names:
                # Filter to common model names
                preferred_patterns = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-2']
                for pattern in preferred_patterns:
                    matching = [m for m in available_model_names if pattern in m.lower()]
                    models_to_try.extend(matching[:2])  # Add up to 2 matches per pattern
            
            # Add fallback models (without 'models/' prefix first)
            fallback_models = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-pro',
            ]
            models_to_try.extend([m for m in fallback_models if m not in models_to_try])
            
            # Remove duplicates while preserving order
            seen = set()
            models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
            
            logger.info(f"Trying {len(models_to_try)} Gemini models...")
            
            model = None
            working_model = None
            
            for model_name in models_to_try:
                try:
                    logger.debug(f"Trying Gemini model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    # Test with a tiny prompt to verify it works
                    test_response = model.generate_content("Hi", generation_config={'max_output_tokens': 1})
                    working_model = model_name
                    logger.info(f"✅ Found working Gemini model: {model_name}")
                    break
                except Exception as model_error:
                    error_msg = str(model_error)[:150]
                    logger.debug(f"Model {model_name} failed: {error_msg}")
                    continue
            
            if not model:
                error_msg = f"No working Gemini model found. Tried {len(models_to_try)} models."
                if available_model_names:
                    error_msg += f" Available models: {available_model_names[:10]}"
                raise Exception(error_msg)
            
            prompt = self._get_gemini_prompt(data_summary)
            response = model.generate_content(prompt)
            result = response.text
            logger.info(f"✅ Gemini analysis completed (model: {gemini_model})")
            return result
        except Exception as e:
            logger.error(f"Error with Gemini analysis: {e}")
            return None
    
    def analyze_with_chatgpt(self, data_summary: str) -> Optional[str]:
        """Analyze using ChatGPT API"""
        if not self.chatgpt_enabled:
            logger.warning("ChatGPT not enabled")
            return None
        
        try:
            prompt = self._get_chatgpt_prompt(data_summary)
            response = self.chatgpt_client.chat.completions.create(
                model=self.chatgpt_model,
                messages=[
                    {"role": "system", "content": "You are an expert forex trader with decades of experience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            result = response.choices[0].message.content
            logger.info("✅ ChatGPT analysis completed")
            return result
        except Exception as e:
            logger.error(f"Error with ChatGPT analysis: {e}")
            return None
    
    def analyze_with_claude(self, data_summary: str) -> Optional[str]:
        """Analyze using Claude"""
        if not self.claude_enabled:
            logger.warning("Claude not enabled")
            return None
        
        try:
            prompt = self._get_claude_prompt(data_summary)
            # Try primary model first, with fallback
            try:
                message = self.claude_client.messages.create(
                    model=self.claude_model,
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
            except Exception as model_error:
                # Try alternative Claude model
                logger.warning(f"Model {self.claude_model} failed, trying claude-3-5-sonnet-20241022: {model_error}")
                try:
                    message = self.claude_client.messages.create(
                        model='claude-3-5-sonnet-20241022',
                        max_tokens=4000,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )
                except Exception:
                    # Try claude-3-sonnet-20240229 as last resort
                    logger.warning("Trying claude-3-sonnet-20240229")
                    message = self.claude_client.messages.create(
                        model='claude-3-sonnet-20240229',
                        max_tokens=4000,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )
            
            result = message.content[0].text
            logger.info("✅ Claude analysis completed")
            return result
        except Exception as e:
            logger.error(f"Error with Claude analysis: {e}")
            return None
    
    def analyze_all(self, data_summary: str) -> Dict[str, Optional[str]]:
        """
        Run analysis on all enabled LLMs (ChatGPT, Gemini, Claude)
        
        Args:
            data_summary: Summary of forex data from Google Drive
            
        Returns:
            Dictionary with LLM names as keys and analysis results as values
        """
        results = {}
        
        logger.info("Starting LLM analysis...")
        
        # Run analyses (ChatGPT, Gemini, Claude)
        logger.info("Running ChatGPT analysis...")
        results['chatgpt'] = self.analyze_with_chatgpt(data_summary)
        
        logger.info("Running Gemini analysis...")
        results['gemini'] = self.analyze_with_gemini(data_summary)
        
        logger.info("Running Claude analysis...")
        results['claude'] = self.analyze_with_claude(data_summary)
        
        # Log results
        enabled_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"Completed {enabled_count}/3 LLM analyses")
        
        # Log which ones succeeded/failed
        for name, result in results.items():
            if result:
                logger.info(f"✅ {name.upper()} analysis completed successfully")
            else:
                logger.warning(f"❌ {name.upper()} analysis failed or returned no result")
        
        return results

