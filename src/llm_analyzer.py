"""LLM analysis: ChatGPT, Gemini, Claude"""

import os
import time
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import pytz
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
        
    
    def _get_chatgpt_prompt(self, data_summary: str, current_datetime: datetime = None) -> str:
        """Get prompt for ChatGPT"""
        # Get current date/time if not provided
        if current_datetime is None:
            current_datetime = datetime.now(pytz.UTC)
        
        # Ensure timezone-aware
        if current_datetime.tzinfo is None:
            current_datetime = pytz.UTC.localize(current_datetime)
        
        # Format in both UTC and EST/EDT
        est_tz = pytz.timezone('America/New_York')
        current_est = current_datetime.astimezone(est_tz)
        current_utc = current_datetime.astimezone(pytz.UTC)
        
        date_time_info = f"""
IMPORTANT: CURRENT DATE AND TIME
- Current Date (EST/EDT): {current_est.strftime('%Y-%m-%d')}
- Current Time (EST/EDT): {current_est.strftime('%H:%M:%S %Z')}
- Current Date (UTC): {current_utc.strftime('%Y-%m-%d')}
- Current Time (UTC): {current_utc.strftime('%H:%M:%S %Z')}

You MUST use the date above ({current_est.strftime('%Y-%m-%d')}) as the current date for your analysis. Do NOT assume or hallucinate dates. All references to "today", "this date", or upcoming events should be based on {current_est.strftime('%Y-%m-%d')}.

"""
        
        return f"""{date_time_info}As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

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

    def _get_gemini_prompt(self, data_summary: str, current_datetime: datetime = None) -> str:
        """Get prompt for Gemini"""
        # Get current date/time if not provided
        if current_datetime is None:
            current_datetime = datetime.now(pytz.UTC)
        
        # Ensure timezone-aware
        if current_datetime.tzinfo is None:
            current_datetime = pytz.UTC.localize(current_datetime)
        
        # Format in both UTC and EST/EDT
        est_tz = pytz.timezone('America/New_York')
        current_est = current_datetime.astimezone(est_tz)
        current_utc = current_datetime.astimezone(pytz.UTC)
        
        date_time_info = f"""
IMPORTANT: CURRENT DATE AND TIME
- Current Date (EST/EDT): {current_est.strftime('%Y-%m-%d')}
- Current Time (EST/EDT): {current_est.strftime('%H:%M:%S %Z')}
- Current Date (UTC): {current_utc.strftime('%Y-%m-%d')}
- Current Time (UTC): {current_utc.strftime('%H:%M:%S %Z')}

You MUST use the date above ({current_est.strftime('%Y-%m-%d')}) as the current date for your analysis. Do NOT assume or hallucinate dates. All references to "today", "this date", or upcoming events should be based on {current_est.strftime('%Y-%m-%d')}.

"""
        
        return f"""{date_time_info}As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

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

    def _get_claude_prompt(self, data_summary: str, current_datetime: datetime = None) -> str:
        """Get prompt for Claude"""
        # Get current date/time if not provided
        if current_datetime is None:
            current_datetime = datetime.now(pytz.UTC)
        
        # Ensure timezone-aware
        if current_datetime.tzinfo is None:
            current_datetime = pytz.UTC.localize(current_datetime)
        
        # Format in both UTC and EST/EDT
        est_tz = pytz.timezone('America/New_York')
        current_est = current_datetime.astimezone(est_tz)
        current_utc = current_datetime.astimezone(pytz.UTC)
        
        date_time_info = f"""
IMPORTANT: CURRENT DATE AND TIME
- Current Date (EST/EDT): {current_est.strftime('%Y-%m-%d')}
- Current Time (EST/EDT): {current_est.strftime('%H:%M:%S %Z')}
- Current Date (UTC): {current_utc.strftime('%Y-%m-%d')}
- Current Time (UTC): {current_utc.strftime('%H:%M:%S %Z')}

You MUST use the date above ({current_est.strftime('%Y-%m-%d')}) as the current date for your analysis. Do NOT assume or hallucinate dates. All references to "today", "this date", or upcoming events should be based on {current_est.strftime('%Y-%m-%d')}.

"""
        
        return f"""{date_time_info}As an expert forex trader with over 20 years of experience in forex trading, please analyze trading opportunities using BOTH of the following sources:

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

    def analyze_with_gemini(self, data_summary: str, current_datetime: datetime = None) -> Optional[str]:
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
            
            # Use models directly from available_models list (they have correct format)
            models_to_try = []
            
            # Add available models first (they already have /models/ prefix if needed)
            if available_model_names:
                # Prefer newer models (2.5, 2.0) and latest versions
                preferred_patterns = [
                    'gemini-2.5-pro',
                    'gemini-2.0-flash',
                    'gemini-flash-latest',
                    'gemini-pro-latest',
                    'gemini-2.0-flash-001',
                    'gemini-1.5-pro',  # Fallback to older models
                    'gemini-1.5-flash',
                ]
                
                for pattern in preferred_patterns:
                    # Find models matching pattern (case insensitive)
                    matching = [m for m in available_model_names if pattern.lower() in m.lower()]
                    if matching:
                        # Take first match (most specific)
                        models_to_try.append(matching[0])
                        logger.debug(f"Found available model matching '{pattern}': {matching[0]}")
                
                # If no preferred models found, try first few available models
                if not models_to_try and available_model_names:
                    models_to_try = available_model_names[:5]
                    logger.info(f"No preferred models found, trying first available: {models_to_try}")
            
            # Remove duplicates while preserving order
            seen = set()
            models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
            
            logger.info(f"Trying {len(models_to_try)} Gemini models from available list...")
            
            model = None
            working_model = None
            
            for model_name in models_to_try:
                try:
                    logger.debug(f"Trying Gemini model: {model_name}")
                    # Use model name as-is from available list (already has correct format)
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
                error_msg = f"No working Gemini model found. Tried {len(models_to_try)} models from available list."
                if available_model_names:
                    error_msg += f" Available models count: {len(available_model_names)}"
                    error_msg += f" Sample: {available_model_names[:5]}"
                raise Exception(error_msg)
            
            prompt = self._get_gemini_prompt(data_summary, current_datetime)
            
            # Retry logic for quota errors (429) with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    result = response.text
                    logger.info(f"✅ Gemini analysis completed (model: {working_model})")
                    return result
                except Exception as api_error:
                    error_str = str(api_error)
                    # Check if it's a quota/rate limit error (429)
                    is_quota_error = '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower()
                    
                    if is_quota_error and attempt < max_retries - 1:
                        # Exponential backoff: 10s, 20s, 30s
                        retry_delay = (attempt + 1) * 10
                        logger.warning(f"⚠️ Gemini quota/rate limit error (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    elif is_quota_error:
                        logger.error(f"❌ Gemini quota exceeded after {max_retries} attempts. Please check your billing account or wait for quota reset.")
                        raise api_error
                    else:
                        # Not a quota error, re-raise immediately
                        raise api_error
            
            # Should not reach here, but just in case
            return None
        except Exception as e:
            logger.error(f"Error with Gemini analysis: {e}")
            return None
    
    def analyze_with_chatgpt(self, data_summary: str, current_datetime: datetime = None) -> Optional[str]:
        """Analyze using ChatGPT API"""
        if not self.chatgpt_enabled:
            logger.warning("ChatGPT not enabled")
            return None
        
        try:
            prompt = self._get_chatgpt_prompt(data_summary, current_datetime)
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
    
    def analyze_with_claude(self, data_summary: str, current_datetime: datetime = None) -> Optional[str]:
        """Analyze using Claude"""
        if not self.claude_enabled:
            logger.warning("Claude not enabled")
            return None
        
        try:
            prompt = self._get_claude_prompt(data_summary, current_datetime)
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
                # Try alternative Claude models - use working model from diagnostic
                logger.warning(f"Model {self.claude_model} failed, trying claude-3-5-haiku-20241822: {model_error}")
                try:
                    message = self.claude_client.messages.create(
                        model='claude-3-5-haiku-20241822',  # This one WORKS from latest diagnostic!
                        max_tokens=4000,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )
                except Exception:
                    # Try claude-3-5-sonnet-20241022 (corrected date)
                    logger.warning("Trying claude-3-5-sonnet-20241022")
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
                        # Last resort: claude-3-sonnet-20240229
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
    
    def analyze_all(self, data_summary: str, current_datetime: datetime = None) -> Dict[str, Optional[str]]:
        """
        Run analysis on all enabled LLMs (ChatGPT, Gemini, Claude)
        
        Args:
            data_summary: Summary of forex data from Google Drive
            current_datetime: Current datetime (defaults to now, in UTC)
            
        Returns:
            Dictionary with LLM names as keys and analysis results as values
        """
        # Get current datetime if not provided
        if current_datetime is None:
            current_datetime = datetime.now(pytz.UTC)
        
        # Ensure timezone-aware
        if current_datetime.tzinfo is None:
            current_datetime = pytz.UTC.localize(current_datetime)
        
        # Log current date/time for debugging
        est_tz = pytz.timezone('America/New_York')
        current_est = current_datetime.astimezone(est_tz)
        logger.info(f"Starting LLM analysis at {current_est.strftime('%Y-%m-%d %H:%M:%S %Z')} (EST/EDT)")
        
        results = {}
        
        # Run analyses (ChatGPT, Gemini, Claude)
        logger.info("Running ChatGPT analysis...")
        results['chatgpt'] = self.analyze_with_chatgpt(data_summary, current_datetime)
        
        logger.info("Running Gemini analysis...")
        results['gemini'] = self.analyze_with_gemini(data_summary, current_datetime)
        
        logger.info("Running Claude analysis...")
        results['claude'] = self.analyze_with_claude(data_summary, current_datetime)
        
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

