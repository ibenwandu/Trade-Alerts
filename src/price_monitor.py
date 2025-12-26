"""Monitor real-time currency prices"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv
from src.logger import setup_logger

load_dotenv()
logger = setup_logger()

class PriceMonitor:
    """Monitor current market prices"""
    
    def __init__(self, base_url: str = None):
        """
        Initialize price monitor
        
        Args:
            base_url: API URL for getting exchange rates
        """
        self.base_url = base_url or os.getenv(
            'PRICE_API_URL',
            'https://api.exchangerate-api.com/v4/latest/USD'
        )
        self.cache = {}
        self.cache_time = 0
        self.cache_ttl = 60  # Cache for 60 seconds
    
    def get_rate(self, pair: str) -> Optional[float]:
        """
        Get current exchange rate for a currency pair
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            
        Returns:
            Exchange rate or None if failed
        """
        try:
            # Normalize pair
            base, quote = pair.split('/')
            
            # Use USD as base currency for API
            if base == 'USD':
                # Direct rate: USD/XXX
                rate = self._get_usd_rate(quote)
                return rate if rate else None
            elif quote == 'USD':
                # Inverse rate: XXX/USD
                rate = self._get_usd_rate(base)
                return 1.0 / rate if rate else None
            else:
                # Cross rate: XXX/YYY = (USD/YYY) / (USD/XXX)
                rate_base = self._get_usd_rate(base)
                rate_quote = self._get_usd_rate(quote)
                if rate_base and rate_quote:
                    return rate_quote / rate_base
                return None
        except Exception as e:
            logger.error(f"Error getting rate for {pair}: {e}")
            return None
    
    def _get_usd_rate(self, currency: str) -> Optional[float]:
        """Get USD/XXX rate"""
        import time
        
        # Check cache
        current_time = time.time()
        if currency in self.cache and (current_time - self.cache_time) < self.cache_ttl:
            return self.cache[currency]
        
        try:
            response = requests.get(self.base_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data:
                rates = data['rates']
                if currency in rates:
                    rate = float(rates[currency])
                    # Update cache
                    self.cache = rates
                    self.cache_time = current_time
                    return rate
                else:
                    logger.warning(f"Currency {currency} not found in API response")
            else:
                logger.warning("API response missing 'rates' key")
        except Exception as e:
            logger.error(f"Error fetching rates from API: {e}")
        
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

