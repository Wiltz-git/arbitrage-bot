"""
Dashboard Sync Module for Crypto Arbitrage Bot

This module handles syncing trade data, opportunities, and summaries
to the remote dashboard hosted on Abacus.AI.

Usage:
    from dashboard_sync import DashboardSync
    
    sync = DashboardSync()
    sync.send_trade(trade_data)
    sync.send_opportunity(opportunity_data)
    sync.send_daily_summary(summary_data)
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DashboardSync:
    """Handles syncing data to the remote dashboard."""
    
    def __init__(self):
        self.dashboard_url = os.getenv('DASHBOARD_URL', '').rstrip('/')
        self.api_key = os.getenv('DASHBOARD_SYNC_API_KEY', '')
        self.enabled = os.getenv('DASHBOARD_SYNC_ENABLED', 'true').lower() == 'true'
        self.timeout = int(os.getenv('DASHBOARD_SYNC_TIMEOUT', '10'))
        
        # Endpoint
        self.sync_endpoint = f"{self.dashboard_url}/api/bot-sync"
        
        # Batch queue for efficient syncing
        self._opportunity_queue: List[Dict] = []
        self._batch_size = 50  # Send opportunities in batches
        
        if self.enabled and self.dashboard_url and self.api_key:
            logger.info(f"Dashboard sync enabled: {self.dashboard_url}")
        elif self.enabled:
            logger.warning("Dashboard sync enabled but URL or API key not configured")
            self.enabled = False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            'Content-Type': 'application/json',
            'X-Bot-API-Key': self.api_key
        }
    
    def _send_request(self, payload: Dict[str, Any]) -> bool:
        """Send a sync request to the dashboard."""
        if not self.enabled:
            return False
        
        try:
            response = requests.post(
                self.sync_endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.debug(f"Dashboard sync successful: {response.json()}")
                return True
            else:
                logger.error(f"Dashboard sync failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning("Dashboard sync timeout - will retry later")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning("Dashboard connection error - will retry later")
            return False
        except Exception as e:
            logger.error(f"Dashboard sync error: {e}")
            return False
    
    def send_trade(self, trade: Dict[str, Any]) -> bool:
        """
        Send a single trade to the dashboard.
        
        Args:
            trade: Dictionary containing trade data with keys:
                - timestamp: ISO format datetime string
                - symbol: Trading pair (e.g., 'BTC/USDT')
                - buy_exchange: Exchange bought from
                - sell_exchange: Exchange sold to
                - buy_price: Buy price
                - sell_price: Sell price
                - trade_amount: Amount traded in USD
                - gross_profit: Profit before fees
                - fees: Total fees
                - net_profit: Profit after fees
                - profit_percentage: Profit as percentage
                - balance_after: Balance after trade
        
        Returns:
            bool: True if sync successful
        """
        payload = {
            'type': 'trade',
            'data': self._normalize_trade(trade),
            'timestamp': datetime.utcnow().isoformat()
        }
        return self._send_request(payload)
    
    def send_opportunity(self, opportunity: Dict[str, Any], immediate: bool = False) -> bool:
        """
        Queue an opportunity for syncing (or send immediately).
        
        Args:
            opportunity: Dictionary containing opportunity data
            immediate: If True, send immediately instead of batching
        
        Returns:
            bool: True if queued/sent successfully
        """
        normalized = self._normalize_opportunity(opportunity)
        
        if immediate:
            payload = {
                'type': 'opportunity',
                'data': normalized,
                'timestamp': datetime.utcnow().isoformat()
            }
            return self._send_request(payload)
        
        # Add to batch queue
        self._opportunity_queue.append(normalized)
        
        # Send batch if queue is full
        if len(self._opportunity_queue) >= self._batch_size:
            return self.flush_opportunities()
        
        return True
    
    def flush_opportunities(self) -> bool:
        """Send all queued opportunities to the dashboard."""
        if not self._opportunity_queue:
            return True
        
        payload = {
            'type': 'batch',
            'opportunities': self._opportunity_queue.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        success = self._send_request(payload)
        if success:
            self._opportunity_queue.clear()
        
        return success
    
    def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """
        Send daily summary to the dashboard.
        
        Args:
            summary: Dictionary containing:
                - date: Date string (YYYY-MM-DD)
                - opportunities_detected: Total opportunities found
                - opportunities_meeting: Opportunities meeting threshold
                - trades_executed: Number of trades made
                - total_profit: Total profit for the day
                - start_balance: Balance at start of day
                - end_balance: Balance at end of day
        
        Returns:
            bool: True if sync successful
        """
        payload = {
            'type': 'daily_summary',
            'data': summary,
            'timestamp': datetime.utcnow().isoformat()
        }
        return self._send_request(payload)
    
    def send_batch(self, trades: List[Dict] = None, 
                   opportunities: List[Dict] = None,
                   daily_summary: Dict = None) -> bool:
        """
        Send multiple items in a single request.
        
        Args:
            trades: List of trade dictionaries
            opportunities: List of opportunity dictionaries
            daily_summary: Daily summary dictionary
        
        Returns:
            bool: True if sync successful
        """
        payload = {
            'type': 'batch',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if trades:
            payload['trades'] = [self._normalize_trade(t) for t in trades]
        
        if opportunities:
            payload['opportunities'] = [self._normalize_opportunity(o) for o in opportunities]
        
        if daily_summary:
            payload['daily_summary'] = daily_summary
        
        return self._send_request(payload)
    
    def heartbeat(self) -> bool:
        """Send a heartbeat to verify connection."""
        payload = {
            'type': 'heartbeat',
            'bot_version': '2.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        return self._send_request(payload)
    
    def check_status(self) -> Optional[Dict]:
        """Check dashboard API status (no auth required)."""
        try:
            response = requests.get(
                self.sync_endpoint,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        return None
    
    def _normalize_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize trade data for API."""
        return {
            'timestamp': trade.get('timestamp', datetime.utcnow().isoformat()),
            'symbol': trade.get('symbol', ''),
            'buy_exchange': trade.get('buy_exchange', ''),
            'sell_exchange': trade.get('sell_exchange', ''),
            'buy_price': float(trade.get('buy_price', 0)),
            'sell_price': float(trade.get('sell_price', 0)),
            'trade_amount': float(trade.get('trade_amount', 0)),
            'gross_profit': float(trade.get('gross_profit', 0)),
            'fees': float(trade.get('fees', 0)),
            'net_profit': float(trade.get('net_profit', 0)),
            'profit_percentage': float(trade.get('profit_percentage', 0)),
            'balance_after': float(trade.get('balance_after', 0)),
            'source': trade.get('source', 'paper')
        }
    
    def _normalize_opportunity(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize opportunity data for API."""
        return {
            'timestamp': opp.get('timestamp', datetime.utcnow().isoformat()),
            'symbol': opp.get('symbol', ''),
            'buy_exchange': opp.get('buy_exchange', ''),
            'sell_exchange': opp.get('sell_exchange', ''),
            'buy_price': float(opp.get('buy_price', 0)),
            'sell_price': float(opp.get('sell_price', 0)),
            'profit_percent': float(opp.get('profit_percent', opp.get('profit_percentage', 0))),
            'meets_threshold': bool(opp.get('meets_threshold', False)),
            'executed': bool(opp.get('executed', False))
        }


# Global instance for easy access
_sync_instance: Optional[DashboardSync] = None

def get_dashboard_sync() -> DashboardSync:
    """Get or create the global DashboardSync instance."""
    global _sync_instance
    if _sync_instance is None:
        _sync_instance = DashboardSync()
    return _sync_instance


# Convenience functions
def sync_trade(trade: Dict[str, Any]) -> bool:
    """Sync a trade to the dashboard."""
    return get_dashboard_sync().send_trade(trade)

def sync_opportunity(opportunity: Dict[str, Any], immediate: bool = False) -> bool:
    """Sync an opportunity to the dashboard."""
    return get_dashboard_sync().send_opportunity(opportunity, immediate)

def sync_daily_summary(summary: Dict[str, Any]) -> bool:
    """Sync daily summary to the dashboard."""
    return get_dashboard_sync().send_daily_summary(summary)

def flush_sync() -> bool:
    """Flush any pending sync data."""
    return get_dashboard_sync().flush_opportunities()
