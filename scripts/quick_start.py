#!/usr/bin/env python3
"""
Quick start script for TradeMind whale tracking

This script demonstrates basic whale tracking functionality
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import config
from src.trademind.monitors.whale_tracker import WhaleTracker
from src.trademind.utils.logger import setup_logger

def main():
    """Quick start demonstration"""
    # Setup logging
    logger = setup_logger(level=config.LOG_LEVEL, log_file=config.LOG_FILE)
    
    try:
        # Validate configuration
        config.validate_config()
        logger.info("✅ Configuration validated successfully")
        
        # Initialize whale tracker
        tracker = WhaleTracker(
            api_key=config.BSCSCAN_API_KEY,
            whale_threshold_usd=config.WHALE_THRESHOLD_USD,
            exchange_addresses=config.EXCHANGE_ADDRESSES
        )
        
        logger.info(f"🐋 Whale tracker initialized (threshold: ${config.WHALE_THRESHOLD_USD:,})")
        logger.info("🔍 Scanning for recent USDT whale transactions on BSC...")
        
        # Scan for whale transactions
        whale_transactions = tracker.scan_recent_transactions_sync(
            contract_address=config.BSC_USDT_CONTRACT,
            token_price_usd=1.0,  # USDT = $1
            limit=50
        )
        
        if whale_transactions:
            logger.info(f"🎯 Found {len(whale_transactions)} whale transactions")
            
            for tx in whale_transactions[:5]:  # Show top 5
                alert = tracker.format_whale_alert(tx)
                print("\n" + "="*50)
                print(alert)
                
        else:
            logger.info("📊 No whale transactions found in recent history")
            logger.info("💡 Try adjusting the whale threshold or check more transactions")
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.info("💡 Please check your .env file and API keys")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())