"""Parse Gemini final recommendations to extract entry/exit points"""

import re
import json
from typing import List, Dict, Optional
from src.logger import setup_logger

logger = setup_logger()

class RecommendationParser:
    """Parse Gemini final synthesis to extract trading recommendations"""
    
    def __init__(self):
        """Initialize parser"""
        self.currency_pairs = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD',
            'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'EUR/AUD',
            'EUR/CAD', 'GBP/AUD', 'GBP/CAD', 'AUD/NZD', 'CAD/CHF', 'EUR/CHF',
            'GBP/CHF', 'AUD/CHF', 'NZD/CHF', 'CAD/JPY', 'CHF/JPY', 'NZD/JPY'
        ]
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        Parse analysis file to extract trading opportunities
        
        Args:
            file_path: Path to analysis file (text or JSON)
            
        Returns:
            List of trading opportunity dictionaries
        """
        return self._parse_text(text)
    
    def _parse_json(self, data: Dict) -> List[Dict]:
        """Parse JSON format analysis"""
        opportunities = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            for item in data:
                opp = self._extract_opportunity_from_dict(item)
                if opp:
                    opportunities.append(opp)
        elif isinstance(data, dict):
            # Look for recommendations or opportunities key
            if 'recommendations' in data:
                for item in data['recommendations']:
                    opp = self._extract_opportunity_from_dict(item)
                    if opp:
                        opportunities.append(opp)
            elif 'opportunities' in data:
                for item in data['opportunities']:
                    opp = self._extract_opportunity_from_dict(item)
                    if opp:
                        opportunities.append(opp)
            else:
                opp = self._extract_opportunity_from_dict(data)
                if opp:
                    opportunities.append(opp)
        
        return opportunities
    
    def _parse_text(self, text: str) -> List[Dict]:
        """Parse text format analysis"""
        opportunities = []
        
        # Find currency pairs mentioned
        for pair in self.currency_pairs:
            pair_pattern = pair.replace('/', '[/ ]')
            pair_section = re.search(
                rf'{pair_pattern}.*?(?=\n\n|\n[A-Z]{{3}}[/ ]|$)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            
            if pair_section:
                section_text = pair_section.group(0)
                opp = self._extract_opportunity_from_text(pair, section_text)
                if opp:
                    opportunities.append(opp)
        
        return opportunities
    
    def _extract_opportunity_from_dict(self, data: Dict) -> Optional[Dict]:
        """Extract opportunity from dictionary"""
        try:
            pair = data.get('pair') or data.get('currency_pair') or data.get('symbol')
            entry = data.get('entry') or data.get('entry_price') or data.get('entryPrice')
            exit_long = data.get('exit') or data.get('exit_price') or data.get('exitPrice') or data.get('target')
            stop_loss = data.get('stop_loss') or data.get('stopLoss') or data.get('stop')
            direction = data.get('direction') or data.get('type') or data.get('action', 'BUY').upper()
            position_size = data.get('position_size') or data.get('positionSize') or data.get('size')
            recommendation = data.get('recommendation') or data.get('reason') or data.get('analysis', '')
            
            if pair and entry:
                # Normalize pair format
                pair = self._normalize_pair(pair)
                if pair:
                    return {
                        'pair': pair,
                        'entry': float(entry),
                        'exit': float(exit_long) if exit_long else None,
                        'stop_loss': float(stop_loss) if stop_loss else None,
                        'direction': 'BUY' if direction in ['BUY', 'LONG', 'GO LONG'] else 'SELL',
                        'position_size': position_size,
                        'recommendation': str(recommendation),
                        'source': 'structured_data'
                    }
        except Exception as e:
            logger.debug(f"Error extracting from dict: {e}")
        
        return None
    
    def _extract_opportunity_from_text(self, pair: str, text: str) -> Optional[Dict]:
        """Extract opportunity from text section"""
        try:
            # Extract entry price
            entry_patterns = [
                r'entry[:\s]+([0-9]+\.?[0-9]*)',
                r'enter[:\s]+(?:at|@)?\s*([0-9]+\.?[0-9]*)',
                r'buy[:\s]+(?:at|@)?\s*([0-9]+\.?[0-9]*)',
                r'sell[:\s]+(?:at|@)?\s*([0-9]+\.?[0-9]*)',
                r'entry\s+price[:\s]+([0-9]+\.?[0-9]*)'
            ]
            
            entry = None
            for pattern in entry_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entry = float(match.group(1))
                    break
            
            # Extract exit/target price
            exit_patterns = [
                r'exit[:\s]+([0-9]+\.?[0-9]*)',
                r'target[:\s]+([0-9]+\.?[0-9]*)',
                r'take[-\s]?profit[:\s]+([0-9]+\.?[0-9]*)',
                r'tp[:\s]+([0-9]+\.?[0-9]*)'
            ]
            
            exit_price = None
            for pattern in exit_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    exit_price = float(match.group(1))
                    break
            
            # Extract stop loss
            stop_patterns = [
                r'stop[-\s]?loss[:\s]+([0-9]+\.?[0-9]*)',
                r'sl[:\s]+([0-9]+\.?[0-9]*)',
                r'stop[:\s]+([0-9]+\.?[0-9]*)'
            ]
            
            stop_loss = None
            for pattern in stop_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    stop_loss = float(match.group(1))
                    break
            
            # Determine direction
            direction = 'BUY'
            if re.search(r'\bsell\b|\bshort\b|\bbearish\b', text, re.IGNORECASE):
                direction = 'SELL'
            
            # Extract position size if mentioned
            size_patterns = [
                r'position[-\s]?size[:\s]+([0-9]+\.?[0-9]*)',
                r'size[:\s]+([0-9]+\.?[0-9]*)',
                r'risk[:\s]+([0-9]+\.?[0-9]*)%'
            ]
            
            position_size = None
            for pattern in size_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    position_size = match.group(1)
                    break
            
            if entry:
                return {
                    'pair': pair,
                    'entry': float(entry),
                    'exit': float(exit_price) if exit_price else None,
                    'stop_loss': float(stop_loss) if stop_loss else None,
                    'direction': direction,
                    'position_size': position_size,
                    'recommendation': text[:500],  # First 500 chars
                    'source': 'text_parsing'
                }
        except Exception as e:
            logger.debug(f"Error extracting from text: {e}")
        
        return None
    
    def _normalize_pair(self, pair: str) -> Optional[str]:
        """Normalize currency pair format (e.g., EURUSD -> EUR/USD)"""
        # Remove spaces and convert to uppercase
        pair = pair.replace(' ', '').replace('_', '/').upper()
        
        # If no slash, try to insert one (assuming 6 chars: EURUSD)
        if '/' not in pair and len(pair) == 6:
            pair = f"{pair[:3]}/{pair[3:]}"
        
        # Check if it's a known pair
        if pair in self.currency_pairs:
            return pair
        
        # Try to match partial (e.g., EURUSD matches EUR/USD)
        for known_pair in self.currency_pairs:
            if pair.replace('/', '') == known_pair.replace('/', ''):
                return known_pair
        
        return None

