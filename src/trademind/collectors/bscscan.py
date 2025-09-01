"""
BSCScan API client for collecting blockchain data
"""
import time
import asyncio
import aiohttp
import requests
from typing import List, Dict, Optional, Union
from datetime import datetime

class BSCScanClient:
    """Client for interacting with BSCScan API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bscscan.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.rate_limit_delay = 0.25  # 250ms between calls (4 calls/sec max)
        self.last_call_time = 0
        
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
            time.sleep(self.rate_limit_delay - time_since_last_call)
            
        self.last_call_time = time.time()
    
    def _build_url(self, params: Dict) -> str:
        """Build API URL with parameters"""
        params['apikey'] = self.api_key
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{param_string}"
    
    async def _make_request(self, params: Dict) -> Dict:
        """Make async API request with rate limiting"""
        self._rate_limit()
        
        if not self.session:
            raise RuntimeError("Client must be used as async context manager")
            
        url = self._build_url(params)
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('status') == '1':
                    return data
                else:
                    raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"HTTP Error: {response.status}")
    
    def _make_sync_request(self, params: Dict) -> Dict:
        """Make synchronous API request with rate limiting"""
        self._rate_limit()
        
        url = self._build_url(params)
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1':
                return data
            else:
                raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
        else:
            raise Exception(f"HTTP Error: {response.status_code}")
    
    async def get_token_transfers(
        self, 
        contract_address: str, 
        start_block: int = 0,
        end_block: int = 999999999,
        page: int = 1,
        offset: int = 100
    ) -> List[Dict]:
        """Get token transfer events for a contract"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': contract_address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc'  # Most recent first
        }
        
        result = await self._make_request(params)
        return result.get('result', [])
    
    def get_token_transfers_sync(
        self,
        contract_address: str,
        start_block: int = 0,
        end_block: int = 999999999,
        page: int = 1,
        offset: int = 100
    ) -> List[Dict]:
        """Synchronous version of get_token_transfers"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': contract_address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc'
        }
        
        result = self._make_sync_request(params)
        return result.get('result', [])
    
    async def get_account_balance(self, address: str) -> float:
        """Get BNB balance for an address"""
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest'
        }
        
        result = await self._make_request(params)
        # Convert wei to BNB
        balance_wei = int(result.get('result', '0'))
        return balance_wei / 10**18
    
    def parse_transaction(self, tx: Dict) -> Dict:
        """Parse and enrich transaction data"""
        try:
            value_wei = int(tx.get('value', '0'))
            decimals = int(tx.get('tokenDecimal', '18'))
            value_tokens = value_wei / (10 ** decimals)
            
            return {
                'hash': tx.get('hash'),
                'from_address': tx.get('from'),
                'to_address': tx.get('to'),
                'contract_address': tx.get('contractAddress'),
                'token_symbol': tx.get('tokenSymbol'),
                'token_name': tx.get('tokenName'),
                'value_raw': value_wei,
                'value_tokens': value_tokens,
                'timestamp': datetime.fromtimestamp(int(tx.get('timeStamp', '0'))),
                'block_number': int(tx.get('blockNumber', '0')),
                'gas_price': int(tx.get('gasPrice', '0')),
                'gas_used': int(tx.get('gasUsed', '0')),
            }
        except (ValueError, TypeError) as e:
            print(f"Error parsing transaction {tx.get('hash', 'unknown')}: {e}")
            return None