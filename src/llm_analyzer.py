"""LLM analysis: ChatGPT, Gemini, Claude"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

# Gemini
try:
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

class LLMAnalyzer:
    """Analyze forex data using multiple LLMs"""
    
    def __init__(self):
        """Initialize LLM analyzers"""
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
        return f"""I want you to review the following report and advise and provide a critique or confirmation based on your knowledge as an expert forex trader with many decades experience and access to all the information that could affect the performance of currencies, crypto and stock market. While the report is based on different resources I want you to do your own research of the current trends in currencies and fact-check the information based on your own research and evaluate the recommendations provided in the report.

FOREX DATA FROM GOOGLE DRIVE:
{data_summary}

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices
- Exit/target prices
- Stop loss levels
- Position sizing recommendations
- Rationale for each recommendation
"""

    def _get_gemini_prompt(self, data_summary: str) -> str:
        """Get prompt for Gemini"""
        return f"""I want you to review the following report and advise and provide a critique or confirmation based on your knowledge as an expert forex trader with many decades experience and access to all the information that could affect the performance of currencies, crypto and stock market. While the report is based on different resources I want you to do your own research of the current trends in currencies and fact-check the information based on your own research and evaluate the recommendations provided in the report.

FOREX DATA FROM GOOGLE DRIVE:
{data_summary}

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices
- Exit/target prices
- Stop loss levels
- Position sizing recommendations
- Rationale for each recommendation
"""

    def _get_claude_prompt(self, data_summary: str) -> str:
        """Get prompt for Claude"""
        return f"""I want you to review the following report and advise and provide a critique or confirmation based on your knowledge as an expert forex trader with many decades experience and access to all the information that could affect the performance of currencies, crypto and stock market. While the report is based on different resources I want you to do your own research of the current trends in currencies and fact-check the information based on your own research and evaluate the recommendations provided in the report.

FOREX DATA FROM GOOGLE DRIVE:
{data_summary}

Please provide your analysis and recommendations in a clear format with:
- Currency pairs to trade
- Entry prices
- Exit/target prices
- Stop loss levels
- Position sizing recommendations
- Rationale for each recommendation
"""

    def analyze_with_gemini(self, data_summary: str) -> Optional[str]:
        """Analyze using Gemini"""
        if not self.gemini_enabled:
            logger.warning("Gemini not enabled")
            return None
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = self._get_gemini_prompt(data_summary)
            response = model.generate_content(prompt)
            result = response.text
            logger.info("✅ Gemini analysis completed")
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
            message = self.claude_client.messages.create(
                model=self.claude_model,
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
        results['chatgpt'] = self.analyze_with_chatgpt(data_summary)
        results['gemini'] = self.analyze_with_gemini(data_summary)
        results['claude'] = self.analyze_with_claude(data_summary)
        
        enabled_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"Completed {enabled_count}/3 LLM analyses")
        
        return results

