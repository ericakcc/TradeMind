"""
CoinGecko API client for collecting market and social data
"""
import time
import asyncio
import aiohttp
import requests
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from ..utils.logger import setup_logger

class CoinGeckoClient:
    """Client for interacting with CoinGecko API"""
    
    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3"):
        self.base_url = base_url
        self.session = None
        self.rate_limit_delay = 1.2  # 1.2s between calls (50 calls/min free tier)
        self.last_call_time = 0
        self.logger = setup_logger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            time.sleep(sleep_time)
            
        self.last_call_time = time.time()
    
    def _build_url(self, endpoint: str, params: Dict = None) -> str:
        """Build API URL with parameters"""
        url = f"{self.base_url}/{endpoint}"
        if params:
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url += f"?{param_string}"
        return url
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make async API request with rate limiting"""
        self._rate_limit()
        
        if not self.session:
            raise RuntimeError("Client must be used as async context manager")
            
        url = self._build_url(endpoint, params)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limit exceeded
                    self.logger.warning("Rate limit exceeded, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return await self._make_request(endpoint, params)
                else:
                    raise Exception(f"HTTP Error: {response.status}")
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return {}
    
    def _make_sync_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make synchronous API request with rate limiting"""
        self._rate_limit()
        
        url = self._build_url(endpoint, params)
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit exceeded
                self.logger.warning("Rate limit exceeded, waiting...")
                time.sleep(60)  # Wait 1 minute
                return self._make_sync_request(endpoint, params)
            else:
                self.logger.error(f"HTTP Error: {response.status_code}")
                return {}
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return {}
    
    def get_trending_coins(self) -> List[Dict]:
        """Get trending coins from CoinGecko"""
        data = self._make_sync_request("search/trending")
        
        if not data or 'coins' not in data:
            return []
            
        trending = []
        for coin_data in data['coins']:
            coin = coin_data['item']
            trending.append({
                'id': coin.get('id'),
                'symbol': coin.get('symbol'),
                'name': coin.get('name'),
                'market_cap_rank': coin.get('market_cap_rank'),
                'price_btc': coin.get('price_btc'),
                'score': coin.get('score', 0)
            })
            
        return trending
    
    def get_new_coins(self, days: int = 30) -> List[Dict]:
        """Get recently listed coins (approximation using market data)"""
        # CoinGecko doesn't have a direct new coins endpoint, so we'll use coins list
        # and filter by age when possible
        data = self._make_sync_request("coins/markets", {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h,7d'
        })
        
        if not data:
            return []
            
        new_coins = []
        for coin in data:
            # We'll need to get detailed info to check actual listing date
            if coin.get('market_cap') and coin.get('total_volume'):
                new_coins.append(self._parse_market_coin(coin))
                
        return new_coins
    
    def get_coin_details(self, coin_id: str) -> Dict:
        """Get detailed information about a specific coin"""
        data = self._make_sync_request(f"coins/{coin_id}", {
            'localization': 'false',
            'tickers': 'true',
            'market_data': 'true',
            'community_data': 'true',
            'developer_data': 'true',
            'sparkline': 'false'
        })
        
        if not data:
            return {}
            
        return self._parse_coin_details(data)
    
    def get_coin_market_data(self, coin_ids: List[str]) -> List[Dict]:
        """Get market data for multiple coins"""
        if not coin_ids:
            return []
            
        # CoinGecko allows up to 250 coins per request
        ids_string = ','.join(coin_ids[:250])
        
        data = self._make_sync_request("coins/markets", {
            'vs_currency': 'usd',
            'ids': ids_string,
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '1h,24h,7d,30d'
        })
        
        if not data:
            return []
            
        return [self._parse_market_coin(coin) for coin in data]
    
    def _parse_market_coin(self, coin: Dict) -> Dict:
        """Parse market data for a coin"""
        return {
            'id': coin.get('id'),
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name'),
            'current_price': coin.get('current_price', 0),
            'market_cap': coin.get('market_cap', 0),
            'market_cap_rank': coin.get('market_cap_rank'),
            'fully_diluted_valuation': coin.get('fully_diluted_valuation'),
            'total_volume': coin.get('total_volume', 0),
            'high_24h': coin.get('high_24h'),
            'low_24h': coin.get('low_24h'),
            'price_change_24h': coin.get('price_change_24h', 0),
            'price_change_percentage_24h': coin.get('price_change_percentage_24h', 0),
            'price_change_percentage_7d': coin.get('price_change_percentage_7d', 0),
            'circulating_supply': coin.get('circulating_supply'),
            'total_supply': coin.get('total_supply'),
            'max_supply': coin.get('max_supply'),
            'ath': coin.get('ath'),
            'ath_change_percentage': coin.get('ath_change_percentage'),
            'ath_date': coin.get('ath_date'),
            'atl': coin.get('atl'),
            'atl_change_percentage': coin.get('atl_change_percentage'),
            'atl_date': coin.get('atl_date'),
            'last_updated': coin.get('last_updated')
        }
    
    def _parse_coin_details(self, coin: Dict) -> Dict:
        """Parse detailed coin information"""
        market_data = coin.get('market_data', {})
        community_data = coin.get('community_data', {})
        developer_data = coin.get('developer_data', {})
        
        return {
            # Basic info
            'id': coin.get('id'),
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name'),
            'description': coin.get('description', {}).get('en', ''),
            'genesis_date': coin.get('genesis_date'),
            'homepage': coin.get('links', {}).get('homepage', []),
            'blockchain_site': coin.get('links', {}).get('blockchain_site', []),
            
            # Market data
            'current_price': market_data.get('current_price', {}).get('usd', 0),
            'market_cap': market_data.get('market_cap', {}).get('usd', 0),
            'total_volume': market_data.get('total_volume', {}).get('usd', 0),
            'circulating_supply': market_data.get('circulating_supply', 0),
            'total_supply': market_data.get('total_supply', 0),
            
            # Social data
            'twitter_followers': community_data.get('twitter_followers', 0),
            'reddit_subscribers': community_data.get('reddit_subscribers', 0),
            'reddit_active_users_48h': community_data.get('reddit_accounts_active_48h', 0),
            'telegram_users': community_data.get('telegram_channel_user_count', 0),
            'facebook_likes': community_data.get('facebook_likes', 0),
            
            # Developer data
            'github_forks': developer_data.get('forks', 0),
            'github_stars': developer_data.get('stars', 0),
            'github_subscribers': developer_data.get('subscribers', 0),
            'github_commits_4w': developer_data.get('commit_count_4_weeks', 0),
            'github_issues': developer_data.get('closed_issues', 0),
            'github_pull_requests': developer_data.get('pull_requests_merged', 0),
            
            # Price changes
            'price_change_24h': market_data.get('price_change_24h', 0),
            'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
            'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
            'price_change_percentage_30d': market_data.get('price_change_percentage_30d', 0),
            
            'last_updated': coin.get('last_updated')
        }
    
    def search_coins(self, query: str) -> List[Dict]:
        """Search for coins by name or symbol"""
        data = self._make_sync_request("search", {'query': query})
        
        if not data or 'coins' not in data:
            return []
            
        results = []
        for coin in data['coins']:
            results.append({
                'id': coin.get('id'),
                'name': coin.get('name'),
                'symbol': coin.get('symbol', '').upper(),
                'market_cap_rank': coin.get('market_cap_rank'),
                'thumb': coin.get('thumb')
            })
            
        return results
    
    def get_global_data(self) -> Dict:
        """Get global cryptocurrency market data"""
        data = self._make_sync_request("global")
        
        if not data or 'data' not in data:
            return {}
            
        global_data = data['data']
        return {
            'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
            'total_volume_usd': global_data.get('total_volume', {}).get('usd', 0),
            'market_cap_percentage_btc': global_data.get('market_cap_percentage', {}).get('btc', 0),
            'market_cap_percentage_eth': global_data.get('market_cap_percentage', {}).get('eth', 0),
            'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
            'markets': global_data.get('markets', 0)
        }