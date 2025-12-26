"""Monitor real-time currency prices using Frankfurter.app"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

class PriceMonitor:
    """Monitor current market prices using Frankfurter.app (free, no API key)"""
    
    def __init__(self):
        """Initialize price monitor"""
        # Frankfurter.app API (free, no API key needed)
        # Documentation: https://www.frankfurter.app/
        self.base_url = 'https://api.frankfurter.app/latest'
        self.cache = {}
        self.cache_time = 0
        self.cache_ttl = 60  # Cache for 60 seconds
    
    def get_rate(self, pair: str) -> Optional[float]:
        """
        Get current exchange rate for a currency pair using Frankfurter.app
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            
        Returns:
            Exchange rate or None if failed
        """
        try:
            # Normalize pair
            base, quote = pair.split('/')
            
            # Frankfurter.app uses EUR as base, so we need to convert
            # For pairs with EUR, get directly
            if base == 'EUR':
                rate = self._get_frankfurter_rate('EUR', quote)
                return rate if rate else None
            elif quote == 'EUR':
                rate = self._get_frankfurter_rate('EUR', base)
                return 1.0 / rate if rate else None
            else:
                # Cross rate: XXX/YYY = (EUR/YYY) / (EUR/XXX)
                rate_base = self._get_frankfurter_rate('EUR', base)
                rate_quote = self._get_frankfurter_rate('EUR', quote)
                if rate_base and rate_quote:
                    return rate_quote / rate_base
                return None
        except Exception as e:
            logger.error(f"Error getting rate for {pair}: {e}")
            return None
    
    def _get_frankfurter_rate(self, base: str, quote: str) -> Optional[float]:
        """Get exchange rate from Frankfurter.app"""
        import time
        
        # Check cache
        cache_key = f"{base}/{quote}"
        current_time = time.time()
        if cache_key in self.cache and (current_time - self.cache_time) < self.cache_ttl:
            return self.cache[cache_key]
        
        try:
            # Frankfurter.app: https://api.frankfurter.app/latest?from=EUR&to=USD
            url = f"{self.base_url}?from={base}&to={quote}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data and quote in data['rates']:
                rate = float(data['rates'][quote])
                # Update cache
                self.cache[cache_key] = rate
                self.cache_time = current_time
                return rate
            else:
                logger.warning(f"Rate {base}/{quote} not found in API response")
        except Exception as e:
            logger.error(f"Error fetching rate from Frankfurter.app: {e}")
        
        return None
    
    def check_entry_point(self, pair: str, entry_price: float, direction: str,
                         tolerance_pips: float = 10, tolerance_percent: float = 0.1) -> bool:
        """
        Check if current price has hit entry point
        
        Args:
            pair: Currency pair
            entry_price: Target entry price
            direction: 'BUY' or 'SELL'
            tolerance_pips: Tolerance in pips (default: 10)
            tolerance_percent: Tolerance as percentage (default: 0.1%)
            
        Returns:
            True if entry point is hit
        """
        current_price = self.get_rate(pair)
        if not current_price:
            return False
        
        # Calculate tolerance
        # For pairs with JPY, 1 pip = 0.01, for others 1 pip = 0.0001
        if 'JPY' in pair:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        tolerance_absolute = max(
            tolerance_pips * pip_value,
            entry_price * (tolerance_percent / 100.0)
        )
        
        if direction == 'BUY':
            # For BUY, price should be at or below entry
            hit = current_price <= (entry_price + tolerance_absolute)
            logger.debug(f"{pair} BUY check: current={current_price}, entry={entry_price}, hit={hit}")
        else:  # SELL
            # For SELL, price should be at or above entry
            hit = current_price >= (entry_price - tolerance_absolute)
            logger.debug(f"{pair} SELL check: current={current_price}, entry={entry_price}, hit={hit}")
        
        return hit
