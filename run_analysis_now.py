"""Run analysis immediately (for testing)"""

import os
import sys
from dotenv import load_dotenv
from src.drive_reader import DriveReader
from src.data_formatter import DataFormatter
from src.llm_analyzer import LLMAnalyzer
from src.gemini_synthesizer import GeminiSynthesizer
from src.email_sender import EmailSender
from src.recommendation_parser import RecommendationParser
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

def run_analysis():
    """Run analysis workflow immediately"""
    logger.info("=" * 60)
    logger.info("Running Analysis Now (Manual Trigger)")
    logger.info("=" * 60)
    
    # Initialize components
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    if not folder_id:
        logger.error("GOOGLE_DRIVE_FOLDER_ID not set in .env")
        sys.exit(1)
    
    drive_reader = DriveReader(folder_id)
    data_formatter = DataFormatter()
    llm_analyzer = LLMAnalyzer()
    gemini_synthesizer = GeminiSynthesizer()
    email_sender = EmailSender()
    parser = RecommendationParser()
    
    try:
        # Step 1: Read raw data from Google Drive
        logger.info("Step 1: Reading data from Google Drive...")
        if not drive_reader.enabled:
            logger.error("Drive reader not enabled - cannot proceed")
            return
        
        # Get latest reports
        files = drive_reader.get_latest_analysis_files(pattern='summary')
        if not files:
            files = drive_reader.get_latest_analysis_files(pattern='report')
        
        if not files:
            logger.warning("No files found in Google Drive folder")
            return
        
        logger.info(f"Found {len(files)} files in folder")
        
        # Download latest files (top 3 most recent)
        downloaded_files = []
        for file_info in files[:3]:
            file_path = drive_reader.download_file(file_info['id'], file_info['title'])
            if file_path:
                downloaded_files.append(file_path)
        
        if not downloaded_files:
            logger.error("Failed to download any files")
            return
        
        logger.info(f"Downloaded {len(downloaded_files)} files")
        
        # Step 2: Format data for LLMs
        logger.info("Step 2: Formatting data for LLM analysis...")
        data_summary = data_formatter.format_files(downloaded_files)
        logger.info(f"Data summary length: {len(data_summary)} characters")
        
        # Step 3: Analyze with LLMs (ChatGPT, Gemini, Claude)
        logger.info("Step 3: Running LLM analysis (ChatGPT, Gemini, Claude)...")
        llm_recommendations = llm_analyzer.analyze_all(data_summary)
        
        # Step 4: Synthesize with Gemini (final recommendation)
        logger.info("Step 4: Synthesizing final recommendations with Gemini...")
        gemini_final = gemini_synthesizer.synthesize(llm_recommendations)
        
        # Step 5: Send email with all recommendations
        logger.info("Step 5: Sending email with all recommendations...")
        email_sender.send_recommendations(llm_recommendations, gemini_final)
        
        # Step 6: Extract entry/exit points from Gemini final recommendation
        if gemini_final:
            logger.info("Step 6: Extracting entry/exit points from final recommendations...")
            opportunities = parser.parse_text(gemini_final)
            if opportunities:
                logger.info(f"✅ Found {len(opportunities)} trading opportunities:")
                for i, opp in enumerate(opportunities, 1):
                    logger.info(f"  {i}. {opp['pair']} {opp['direction']} @ {opp['entry']}")
            else:
                logger.warning("No entry/exit points extracted from recommendations")
        else:
            logger.warning("No Gemini final synthesis available - cannot extract entry points")
        
        logger.info("=" * 60)
        logger.info("✅ Analysis completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error in analysis workflow: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    run_analysis()

