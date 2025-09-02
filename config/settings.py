"""
Configuration settings for TradeMind
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

class Config:
    """Base configuration"""
    
    # API Keys
    BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
    
    # API Endpoints
    BSCSCAN_API_URL = "https://api.bscscan.com/api"
    ETHERSCAN_API_URL = "https://api.etherscan.io/api"
    
    # External Data APIs
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/v1"
    DEFILLAMA_API_URL = "https://api.llama.fi"
    DEXTOOLS_API_URL = "https://www.dextools.io/shared/data"
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{PROJECT_ROOT}/data/trademind.db')
    
    # Monitoring Settings
    WHALE_THRESHOLD_USD = int(os.getenv('WHALE_THRESHOLD_USD', 100000))
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
    MAX_API_CALLS_PER_SECOND = int(os.getenv('MAX_API_CALLS_PER_SECOND', 4))
    
    # Gem Discovery Settings
    GEM_MIN_MARKET_CAP = int(os.getenv('GEM_MIN_MARKET_CAP', 1_000_000))        # $1M
    GEM_MAX_MARKET_CAP = int(os.getenv('GEM_MAX_MARKET_CAP', 100_000_000))      # $100M
    GEM_MIN_VOLUME_24H = int(os.getenv('GEM_MIN_VOLUME_24H', 100_000))          # $100K
    GEM_MIN_HOLDERS = int(os.getenv('GEM_MIN_HOLDERS', 1000))                   # 1000 holders
    GEM_MAX_AGE_DAYS = int(os.getenv('GEM_MAX_AGE_DAYS', 90))                   # 90 days
    GEM_MIN_AGE_DAYS = int(os.getenv('GEM_MIN_AGE_DAYS', 7))                    # 7 days
    
    # Scoring Weights
    SOCIAL_SCORE_WEIGHT = float(os.getenv('SOCIAL_SCORE_WEIGHT', 0.3))          # 30%
    ONCHAIN_SCORE_WEIGHT = float(os.getenv('ONCHAIN_SCORE_WEIGHT', 0.25))       # 25%
    DEV_SCORE_WEIGHT = float(os.getenv('DEV_SCORE_WEIGHT', 0.2))                # 20%
    LIQUIDITY_SCORE_WEIGHT = float(os.getenv('LIQUIDITY_SCORE_WEIGHT', 0.15))   # 15%
    HOLDER_SCORE_WEIGHT = float(os.getenv('HOLDER_SCORE_WEIGHT', 0.1))          # 10%
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = PROJECT_ROOT / 'logs' / 'trademind.log'
    
    # Contract Addresses
    BSC_USDT_CONTRACT = "0x55d398326f99059fF775485246999027B3197955"
    BSC_BUSD_CONTRACT = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
    
    # Known Exchange Addresses (partial list for learning)
    EXCHANGE_ADDRESSES = {
        # Binance hot wallets
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
        "0xd551234ae421e3bcba99a0da6d736074f22192ff": "Binance",
        "0x564286362092d8e7936f0549571a803b203aaced": "Binance",
        
        # Other major exchanges
        "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKEx",
        "0x46705dfff24256421a05d056c29e81bdc09723b8": "Huobi",
    }
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.BSCSCAN_API_KEY:
            raise ValueError("BSCSCAN_API_KEY is required")
        
        # Create required directories
        (PROJECT_ROOT / 'data').mkdir(exist_ok=True)
        (PROJECT_ROOT / 'logs').mkdir(exist_ok=True)
        
        return True

# Global config instance
config = Config()