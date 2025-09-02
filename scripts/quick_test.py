#!/usr/bin/env python3
"""
Quick test script for TradeMind Gem Discovery System
快速測試 TradeMind 潛力幣發現系統的基本功能
"""
import sys
import os
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trademind.collectors.coingecko import CoinGeckoClient
from src.trademind.analyzers.gem_finder import GemFinder
from src.trademind.analyzers.score_calculator import GemScoreCalculator
from src.trademind.utils.logger import setup_logger

def test_coingecko_connection():
    """測試 CoinGecko API 連接"""
    print("🔌 測試 CoinGecko API 連接...")
    
    try:
        client = CoinGeckoClient()
        
        # 測試獲取全球數據
        global_data = client.get_global_data()
        if global_data:
            print(f"   ✅ 全球市值: ${global_data.get('total_market_cap_usd', 0):,.0f}")
            print(f"   ✅ 活躍加密貨幣: {global_data.get('active_cryptocurrencies', 0):,} 個")
            return True
        else:
            print("   ❌ 無法獲取全球數據")
            return False
            
    except Exception as e:
        print(f"   ❌ API 連接失敗: {e}")
        return False

def test_trending_coins():
    """測試趨勢幣獲取"""
    print("🔥 測試趨勢幣獲取...")
    
    try:
        client = CoinGeckoClient()
        trending = client.get_trending_coins()
        
        if trending:
            print(f"   ✅ 獲取到 {len(trending)} 個趨勢幣")
            for i, coin in enumerate(trending[:3], 1):
                print(f"   {i}. {coin['name']} ({coin['symbol']})")
            return True
        else:
            print("   ❌ 無法獲取趨勢幣數據")
            return False
            
    except Exception as e:
        print(f"   ❌ 趨勢幣獲取失敗: {e}")
        return False

def test_coin_details():
    """測試幣種詳細資訊獲取"""
    print("📊 測試幣種詳細資訊獲取...")
    
    try:
        client = CoinGeckoClient()
        # 測試獲取比特幣詳細資訊
        btc_data = client.get_coin_details('bitcoin')
        
        if btc_data:
            print(f"   ✅ {btc_data['name']} ({btc_data['symbol']})")
            print(f"   💰 價格: ${btc_data.get('current_price', 0):,.2f}")
            print(f"   📊 市值: ${btc_data.get('market_cap', 0):,.0f}")
            print(f"   🐦 Twitter 關注者: {btc_data.get('twitter_followers', 0):,}")
            return True
        else:
            print("   ❌ 無法獲取詳細資訊")
            return False
            
    except Exception as e:
        print(f"   ❌ 詳細資訊獲取失敗: {e}")
        return False

def test_score_calculator():
    """測試評分計算器"""
    print("🧮 測試評分計算器...")
    
    try:
        calculator = GemScoreCalculator()
        
        # 創建測試數據
        test_coin = {
            'name': 'Test Coin',
            'symbol': 'TEST',
            'market_cap': 25_000_000,  # 25M - 在甜蜜點範圍內
            'total_volume': 2_500_000,  # 10% 日成交率
            'current_price': 1.0,
            'twitter_followers': 15000,
            'reddit_subscribers': 8000,
            'reddit_active_users_48h': 150,
            'github_commits_4w': 30,
            'github_stars': 500,
            'price_change_percentage_24h': 5.2,
            'price_change_percentage_7d': 15.8,
            'high_24h': 1.1,
            'low_24h': 0.95,
            'ath': 2.5,
            'circulating_supply': 10_000_000,
            'total_supply': 12_000_000
        }
        
        scores = calculator.calculate_comprehensive_score(test_coin)
        
        if scores:
            print(f"   ✅ 總評分: {scores['risk_adjusted_score']:.1f}/100")
            print(f"   🎯 等級: {scores['grade']}")
            print(f"   💡 建議: {scores['recommendation']}")
            print(f"   ⚠️  風險: {scores['risk_score']:.1f}/100")
            return True
        else:
            print("   ❌ 評分計算失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 評分計算器測試失敗: {e}")
        return False

def test_gem_finder():
    """測試潛力幣發現器（輕量版）"""
    print("💎 測試潛力幣發現器...")
    
    try:
        finder = GemFinder(
            min_market_cap=1_000_000,
            max_market_cap=100_000_000,
            min_volume_24h=50_000,  # 降低門檻以便測試
            min_holders=500,
            max_age_days=90,
            min_age_days=1
        )
        
        # 只測試趨勢幣發現，避免過多 API 調用
        gems = finder.find_trending_gems()
        
        if gems:
            print(f"   ✅ 發現 {len(gems)} 個潛力項目")
            
            if len(gems) > 0:
                best_gem = gems[0]
                print(f"   🏆 最佳項目: {best_gem['name']} ({best_gem['symbol']})")
                print(f"   📊 潛力評分: {best_gem.get('potential_score', 0):.1f}")
            return True
        else:
            print("   ⚠️  未發現潛力項目（可能是篩選條件太嚴格）")
            return True  # 這不算失敗，只是沒找到符合條件的
            
    except Exception as e:
        print(f"   ❌ 潛力幣發現器測試失敗: {e}")
        return False

def test_report_generation():
    """測試報告生成"""
    print("📋 測試報告生成...")
    
    try:
        calculator = GemScoreCalculator()
        finder = GemFinder()
        
        # 使用測試數據
        test_gem = {
            'name': 'Demo Gem',
            'symbol': 'DEMO',
            'market_cap': 15_000_000,
            'total_volume': 1_500_000,
            'current_price': 0.5,
            'potential_score': 75.5,
            'risk_level': 'MEDIUM',
            'recommendation': 'BUY',
            'discovery_source': 'test'
        }
        
        # 測試基本報告格式
        basic_report = finder.format_gem_report(test_gem)
        if len(basic_report) > 100:  # 報告應該有足夠的內容
            print("   ✅ 基礎報告生成成功")
        else:
            print("   ❌ 基礎報告內容不足")
            return False
        
        # 測試詳細評分報告
        scores = calculator.calculate_comprehensive_score(test_gem)
        detailed_report = calculator.generate_score_report(test_gem, scores)
        
        if len(detailed_report) > 100:  # 詳細報告應該有更多內容
            print("   ✅ 詳細報告生成成功")
            return True
        else:
            print("   ❌ 詳細報告內容不足")
            return False
            
    except Exception as e:
        print(f"   ❌ 報告生成測試失敗: {e}")
        return False

def main():
    """運行所有測試"""
    print("🧪 TradeMind 潛力幣發現系統 - 快速測試")
    print("="*60)
    
    logger = setup_logger(level='INFO')
    
    tests = [
        ("CoinGecko API 連接", test_coingecko_connection),
        ("趨勢幣獲取", test_trending_coins),
        ("幣種詳細資訊", test_coin_details),
        ("評分計算器", test_score_calculator),
        ("潛力幣發現器", test_gem_finder),
        ("報告生成", test_report_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n📝 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name} 通過")
            else:
                print(f"   ❌ {test_name} 失敗")
        except Exception as e:
            print(f"   ❌ {test_name} 異常: {e}")
    
    print("\\n" + "="*60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統運行正常")
        print("✨ 您可以運行 'python scripts/gem_discovery_demo.py' 開始尋找潛力幣")
    elif passed >= total * 0.8:
        print("👍 大部分測試通過，系統基本可用")
        print("⚠️  建議檢查失敗的測試項目")
    else:
        print("⚠️  多項測試失敗，請檢查配置和網路連接")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)