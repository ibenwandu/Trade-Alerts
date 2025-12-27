"""Main application: LLM analysis workflow and entry point monitoring"""

import os
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
import pytz
from src.drive_reader import DriveReader
from src.data_formatter import DataFormatter
from src.llm_analyzer import LLMAnalyzer
from src.gemini_synthesizer import GeminiSynthesizer
from src.email_sender import EmailSender
from src.recommendation_parser import RecommendationParser
from src.price_monitor import PriceMonitor
from src.alert_manager import AlertManager
from src.alert_history import AlertHistory
from src.scheduler import AnalysisScheduler
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

class TradeAlertSystem:
    """Main trading alert system"""
    
    def __init__(self):
        """Initialize system"""
        # Configuration
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 60))  # seconds
        
        # Initialize components
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
        if not folder_id:
            logger.error("GOOGLE_DRIVE_FOLDER_ID not set in environment variables")
            logger.error("Please set GOOGLE_DRIVE_FOLDER_ID in Render Dashboard → Environment")
            # Don't exit immediately - let it fail gracefully so we can see the error in logs
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable is required")
        
        self.drive_reader = DriveReader(folder_id)
        self.data_formatter = DataFormatter()
        self.llm_analyzer = LLMAnalyzer()
        self.gemini_synthesizer = GeminiSynthesizer()
        self.email_sender = EmailSender()
        self.parser = RecommendationParser()
        self.price_monitor = PriceMonitor()
        self.alert_manager = AlertManager()
        self.alert_history = AlertHistory()
        self.scheduler = AnalysisScheduler()
        
        # State
        self.opportunities = []
        self.last_analysis_time = None
        
        logger.info("✅ Trade Alert System initialized")
    
    def run(self):
        """Run main loop"""
        logger.info("🚀 Starting Trade Alert System...")
        logger.info("Press Ctrl+C to stop")
        
        # Show next analysis time
        next_analysis = self.scheduler.get_next_analysis_time()
        if next_analysis:
            # Convert to EST for display
            est_tz = pytz.timezone('America/New_York')
            if next_analysis.tzinfo is None:
                next_analysis_utc = pytz.UTC.localize(next_analysis)
            else:
                next_analysis_utc = next_analysis
            next_analysis_est = next_analysis_utc.astimezone(est_tz)
            logger.info(f"⏰ Next scheduled analysis: {next_analysis_est.strftime('%Y-%m-%d %H:%M %Z')} (EST/EDT)")
        else:
            logger.info("⏰ No scheduled analysis times configured")
        
        try:
            check_count = 0
            est_tz = pytz.timezone('America/New_York')
            while True:
                # Get current time in UTC (Render uses UTC)
                current_time = datetime.now(pytz.UTC)
                check_count += 1
                
                # Log status every 10 checks (10 minutes)
                if check_count % 10 == 0:
                    logger.info(f"\n=== Status Check #{check_count} ===")
                    # Show time in EST
                    current_time_est = current_time.astimezone(est_tz)
                    logger.info(f"Current time: {current_time_est.strftime('%H:%M:%S %Z')} (EST/EDT)")
                    logger.info(f"Active opportunities: {len(self.opportunities)}")
                    if next_analysis:
                        # Ensure both times are timezone-aware for calculation
                        if next_analysis.tzinfo is None:
                            next_analysis_utc = pytz.UTC.localize(next_analysis)
                        else:
                            next_analysis_utc = next_analysis
                        time_until = (next_analysis_utc - current_time).total_seconds() / 60
                        if time_until > 0:
                            next_analysis_est = next_analysis_utc.astimezone(est_tz)
                            logger.info(f"Next analysis at: {next_analysis_est.strftime('%H:%M %Z')} (in {int(time_until)} minutes)")
                
                # Check if scheduled analysis time
                if self.scheduler.should_run_analysis(current_time):
                    # Avoid running multiple times in same window
                    if (self.last_analysis_time is None or 
                        (current_time - self.last_analysis_time).total_seconds() > 300):
                        # Show time in EST for logging
                        current_time_est = current_time.astimezone(est_tz)
                        logger.info(f"\n{'='*80}")
                        logger.info(f"=== Scheduled Analysis Time: {current_time_est.strftime('%Y-%m-%d %H:%M:%S %Z')} (EST/EDT) ===")
                        logger.info(f"{'='*80}")
                        try:
                            self._run_full_analysis()
                            logger.info(f"✅ Analysis completed successfully at {current_time_est.strftime('%H:%M:%S %Z')}")
                        except Exception as e:
                            logger.error(f"❌ Analysis failed at {current_time_est.strftime('%H:%M:%S %Z')}: {e}", exc_info=True)
                        self.last_analysis_time = current_time
                        # Update next analysis time
                        next_analysis = self.scheduler.get_next_analysis_time()
                
                # Check entry points continuously
                self._check_entry_points()
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  System stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
            raise
    
    def _run_full_analysis(self):
        """Run full analysis workflow"""
        logger.info("Starting full analysis workflow...")
        
        try:
            # Step 1: Read raw data from Google Drive
            logger.info("Step 1: Reading data from Google Drive...")
            if not self.drive_reader.enabled:
                logger.error("Drive reader not enabled - cannot proceed")
                return
            
            # Get latest reports
            files = self.drive_reader.get_latest_analysis_files(pattern='summary')
            if not files:
                files = self.drive_reader.get_latest_analysis_files(pattern='report')
            
            if not files:
                logger.warning("No files found in Google Drive folder")
                return
            
            # Download latest files (top 3 most recent)
            downloaded_files = []
            for file_info in files[:3]:
                file_path = self.drive_reader.download_file(file_info['id'], file_info['title'])
                if file_path:
                    downloaded_files.append(file_path)
            
            if not downloaded_files:
                logger.error("Failed to download any files")
                return
            
            logger.info(f"Downloaded {len(downloaded_files)} files")
            
            # Step 2: Format data for LLMs
            logger.info("Step 2: Formatting data for LLM analysis...")
            data_summary = self.data_formatter.format_files(downloaded_files)
            
            # Step 3: Analyze with LLMs (ChatGPT, Gemini, Claude)
            logger.info("Step 3: Running LLM analysis (ChatGPT, Gemini, Claude)...")
            # Get current datetime for all LLM calls
            current_datetime = datetime.now(pytz.UTC)
            llm_recommendations = self.llm_analyzer.analyze_all(data_summary, current_datetime)
            
            # Step 4: Synthesize with Gemini (final recommendation)
            logger.info("Step 4: Synthesizing final recommendations with Gemini...")
            gemini_final = self.gemini_synthesizer.synthesize(llm_recommendations, current_datetime)
            
            # Step 5: Send email with all recommendations
            logger.info("Step 5: Sending email with all recommendations...")
            self.email_sender.send_recommendations(llm_recommendations, gemini_final)
            
            # Step 6: Extract entry/exit points from Gemini final recommendation
            if gemini_final:
                logger.info("Step 6: Extracting entry/exit points from final recommendations...")
                new_opportunities = self.parser.parse_text(gemini_final)
                if new_opportunities:
                    logger.info(f"Found {len(new_opportunities)} trading opportunities")
                    self.opportunities = new_opportunities
                else:
                    logger.warning("No entry/exit points extracted from recommendations")
            else:
                logger.warning("No Gemini final synthesis available - cannot extract entry points")
            
            logger.info("✅ Full analysis workflow completed")
            
        except Exception as e:
            logger.error(f"Error in full analysis workflow: {e}", exc_info=True)
    
    def _check_entry_points(self):
        """Check all opportunities for entry points"""
        if not self.opportunities:
            return
        
        logger.debug(f"Checking {len(self.opportunities)} opportunities...")
        
        for opp in self.opportunities:
            try:
                pair = opp['pair']
                entry = opp['entry']
                direction = opp['direction']
                
                # Skip if already alerted
                if self.alert_history.has_alerted(opp):
                    continue
                
                # Get current price
                current_price = self.price_monitor.get_rate(pair)
                if not current_price:
                    continue
                
                # Check if entry point is hit
                hit = self.price_monitor.check_entry_point(
                    pair, entry, direction
                )
                
                if hit:
                    logger.info(f"🚨 ENTRY POINT HIT: {pair} {direction} @ {entry}")
                    
                    # Send alert
                    if self.alert_manager.send_entry_alert(opp, current_price):
                        self.alert_history.record_alert(opp, current_price)
                        logger.info(f"✅ Alert sent for {pair}")
                    
            except Exception as e:
                logger.error(f"Error checking opportunity {opp.get('pair', 'unknown')}: {e}")

def main():
    """Main entry point"""
    system = TradeAlertSystem()
    system.run()

if __name__ == '__main__':
    main()
