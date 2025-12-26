"""Schedule analysis at specific times"""

import os
from datetime import datetime, time
from typing import List, Optional
from dotenv import load_dotenv
import pytz
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

class AnalysisScheduler:
    """Manage scheduled analysis times"""
    
    def __init__(self):
        """Initialize scheduler"""
        # Default times: 7am, 9am, 12pm, 4pm EST
        default_times = "07:00,09:00,12:00,16:00"
        times_str = os.getenv('ANALYSIS_TIMES', default_times)
        
        # Get timezone (default to EST/EDT)
        timezone_str = os.getenv('ANALYSIS_TIMEZONE', 'America/New_York')
        try:
            self.timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {timezone_str}, using EST/EDT")
            self.timezone = pytz.timezone('America/New_York')
        
        self.scheduled_times = self._parse_times(times_str)
        logger.info(f"Analysis scheduled for: {[t.strftime('%H:%M') for t in self.scheduled_times]} ({timezone_str})")
    
    def _parse_times(self, times_str: str) -> List[time]:
        """Parse comma-separated time string into time objects"""
        times = []
        for time_str in times_str.split(','):
            time_str = time_str.strip()
            try:
                hour, minute = map(int, time_str.split(':'))
                times.append(time(hour, minute))
            except ValueError:
                logger.warning(f"Invalid time format: {time_str}, skipping")
        return sorted(times)
    
    def should_run_analysis(self, current_time: datetime = None) -> bool:
        """
        Check if analysis should run at current time
        
        Args:
            current_time: Current datetime (defaults to now, in UTC)
            
        Returns:
            True if analysis should run
        """
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # Convert current time to target timezone (EST/EDT)
        if current_time.tzinfo is None:
            # Assume UTC if no timezone info
            current_time = pytz.UTC.localize(current_time)
        
        current_time_est = current_time.astimezone(self.timezone)
        current_time_only = current_time_est.time()
        
        # Check if current time matches any scheduled time (within 5 minutes)
        for scheduled_time in self.scheduled_times:
            if self._times_match(current_time_only, scheduled_time, tolerance_minutes=5):
                return True
        
        return False
    
    def _times_match(self, time1: time, time2: time, tolerance_minutes: int = 5) -> bool:
        """Check if two times match within tolerance"""
        minutes1 = time1.hour * 60 + time1.minute
        minutes2 = time2.hour * 60 + time2.minute
        diff = abs(minutes1 - minutes2)
        return diff <= tolerance_minutes
    
    def get_next_analysis_time(self, current_time: datetime = None) -> Optional[datetime]:
        """
        Get next scheduled analysis time (returns UTC datetime)
        
        Args:
            current_time: Current datetime (defaults to now, in UTC)
            
        Returns:
            Next analysis datetime (in UTC)
        """
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # Convert current time to target timezone (EST/EDT)
        if current_time.tzinfo is None:
            # Assume UTC if no timezone info
            current_time = pytz.UTC.localize(current_time)
        
        current_time_est = current_time.astimezone(self.timezone)
        current_time_only = current_time_est.time()
        current_date_est = current_time_est.date()
        
        # Find next scheduled time today in EST
        for scheduled_time in self.scheduled_times:
            if current_time_only <= scheduled_time:
                # Create datetime in EST timezone
                next_analysis_est = self.timezone.localize(
                    datetime.combine(current_date_est, scheduled_time)
                )
                # Convert to UTC for return
                return next_analysis_est.astimezone(pytz.UTC).replace(tzinfo=None)
        
        # If no time today, use first time tomorrow in EST
        if self.scheduled_times:
            from datetime import timedelta
            tomorrow_est = current_date_est + timedelta(days=1)
            next_analysis_est = self.timezone.localize(
                datetime.combine(tomorrow_est, self.scheduled_times[0])
            )
            # Convert to UTC for return
            return next_analysis_est.astimezone(pytz.UTC).replace(tzinfo=None)
        
        return None

