"""
Whale transaction monitoring and detection
"""
import asyncio
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from ..collectors.bscscan import BSCScanClient

class WhaleTracker:
    """Monitor and detect whale (large) transactions"""
    
    def __init__(self, 
                 api_key: str,
                 whale_threshold_usd: float = 100000,
                 exchange_addresses: Optional[Dict[str, str]] = None):
        self.client = BSCScanClient(api_key)
        self.whale_threshold_usd = whale_threshold_usd
        self.exchange_addresses = exchange_addresses or {}
        self.known_transactions: Set[str] = set()
        self.last_check_block = 0
        
    def is_exchange_address(self, address: str) -> Optional[str]:
        """Check if address belongs to a known exchange"""
        return self.exchange_addresses.get(address.lower())
    
    def classify_transaction(self, tx: Dict) -> Dict:
        """Classify transaction based on addresses and patterns"""
        from_exchange = self.is_exchange_address(tx['from_address'])
        to_exchange = self.is_exchange_address(tx['to_address'])
        
        classification = {
            'from_exchange': from_exchange,
            'to_exchange': to_exchange,
            'direction': None,
            'risk_level': 'MEDIUM'
        }
        
        if from_exchange and not to_exchange:
            classification['direction'] = 'EXCHANGE_OUTFLOW'
            classification['risk_level'] = 'HIGH'  # Often bullish
        elif not from_exchange and to_exchange:
            classification['direction'] = 'EXCHANGE_INFLOW'
            classification['risk_level'] = 'HIGH'  # Often bearish
        elif from_exchange and to_exchange:
            classification['direction'] = 'EXCHANGE_TO_EXCHANGE'
            classification['risk_level'] = 'LOW'
        else:
            classification['direction'] = 'WALLET_TO_WALLET'
            classification['risk_level'] = 'MEDIUM'
            
        return classification
    
    def is_whale_transaction(self, tx: Dict, token_price_usd: float = 1.0) -> bool:
        """Determine if transaction qualifies as whale activity"""
        usd_value = tx['value_tokens'] * token_price_usd
        return usd_value >= self.whale_threshold_usd
    
    async def scan_recent_transactions(self, 
                                     contract_address: str,
                                     token_price_usd: float = 1.0,
                                     limit: int = 100) -> List[Dict]:
        """Scan for recent whale transactions"""
        whale_transactions = []
        
        async with self.client as client:
            transactions = await client.get_token_transfers(
                contract_address=contract_address,
                offset=limit
            )
            
            for tx_data in transactions:
                tx = client.parse_transaction(tx_data)
                if not tx or tx['hash'] in self.known_transactions:
                    continue
                    
                if self.is_whale_transaction(tx, token_price_usd):
                    tx['classification'] = self.classify_transaction(tx)
                    tx['usd_value'] = tx['value_tokens'] * token_price_usd
                    whale_transactions.append(tx)
                    self.known_transactions.add(tx['hash'])
                    
        return whale_transactions
    
    def scan_recent_transactions_sync(self,
                                    contract_address: str,
                                    token_price_usd: float = 1.0,
                                    limit: int = 100) -> List[Dict]:
        """Synchronous version of scan_recent_transactions"""
        whale_transactions = []
        
        transactions = self.client.get_token_transfers_sync(
            contract_address=contract_address,
            offset=limit
        )
        
        for tx_data in transactions:
            tx = self.client.parse_transaction(tx_data)
            if not tx or tx['hash'] in self.known_transactions:
                continue
                
            if self.is_whale_transaction(tx, token_price_usd):
                tx['classification'] = self.classify_transaction(tx)
                tx['usd_value'] = tx['value_tokens'] * token_price_usd
                whale_transactions.append(tx)
                self.known_transactions.add(tx['hash'])
                
        return whale_transactions
    
    def format_whale_alert(self, tx: Dict) -> str:
        """Format whale transaction for alerting"""
        direction = tx['classification']['direction']
        risk = tx['classification']['risk_level']
        
        alert = f"🐋 WHALE ALERT [{risk}]\n"
        alert += f"💰 {tx['usd_value']:,.0f} USD ({tx['value_tokens']:,.2f} {tx['token_symbol']})\n"
        alert += f"📊 {direction.replace('_', ' ').title()}\n"
        alert += f"🔗 From: {tx['from_address'][:8]}...{tx['from_address'][-6:]}\n"
        alert += f"🔗 To: {tx['to_address'][:8]}...{tx['to_address'][-6:]}\n"
        
        if tx['classification']['from_exchange']:
            alert += f"🏪 From: {tx['classification']['from_exchange']}\n"
        if tx['classification']['to_exchange']:
            alert += f"🏪 To: {tx['classification']['to_exchange']}\n"
            
        alert += f"⏰ {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        alert += f"🔍 Hash: {tx['hash'][:16]}...\n"
        
        return alert