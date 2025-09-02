#!/usr/bin/env python3
"""
Gem Discovery System Demo
演示潛力幣發現系統的完整功能
"""
import sys
import os
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import config
from src.trademind.analyzers.gem_finder import GemFinder
from src.trademind.analyzers.score_calculator import GemScoreCalculator
from src.trademind.utils.logger import setup_logger

def main():
    """潛力幣發現系統演示"""
    logger = setup_logger(level=config.LOG_LEVEL)
    
    print("🚀 TradeMind 潛力幣發現系統 v1.0")
    print("="*60)
    print("正在初始化系統...")
    
    try:
        # 初始化組件
        gem_finder = GemFinder(
            min_market_cap=config.GEM_MIN_MARKET_CAP,
            max_market_cap=config.GEM_MAX_MARKET_CAP,
            min_volume_24h=config.GEM_MIN_VOLUME_24H,
            min_holders=config.GEM_MIN_HOLDERS,
            max_age_days=config.GEM_MAX_AGE_DAYS,
            min_age_days=config.GEM_MIN_AGE_DAYS
        )
        
        score_calculator = GemScoreCalculator(
            social_weight=config.SOCIAL_SCORE_WEIGHT,
            onchain_weight=config.ONCHAIN_SCORE_WEIGHT,
            dev_weight=config.DEV_SCORE_WEIGHT,
            liquidity_weight=config.LIQUIDITY_SCORE_WEIGHT,
            holder_weight=config.HOLDER_SCORE_WEIGHT
        )
        
        print("✅ 系統初始化完成")
        print("🔍 開始搜尋潛力幣...")
        print("-"*60)
        
        # 運行不同的發現策略
        all_gems = []
        
        print("\n1️⃣ 搜尋趨勢潛力幣...")
        trending_gems = gem_finder.find_trending_gems()
        all_gems.extend(trending_gems)
        
        print(f"   發現 {len(trending_gems)} 個趨勢潛力項目")
        
        print("\n2️⃣ 搜尋新上線潛力幣...")
        new_gems = gem_finder.find_new_listings()
        all_gems.extend(new_gems)
        
        print(f"   發現 {len(new_gems)} 個新上線潛力項目")
        
        print("\n3️⃣ 搜尋交易量異常潛力幣...")
        volume_gems = gem_finder.find_volume_surge_gems()
        all_gems.extend(volume_gems)
        
        print(f"   發現 {len(volume_gems)} 個交易量異常潛力項目")
        
        print("\n4️⃣ 搜尋社交媒體熱度潛力幣...")
        social_gems = gem_finder.find_social_buzz_gems()
        all_gems.extend(social_gems)
        
        print(f"   發現 {len(social_gems)} 個社交熱度潛力項目")
        
        # 去重並計算詳細評分
        unique_gems = gem_finder._deduplicate_gems(all_gems)
        
        print(f"\\n📊 總共發現 {len(unique_gems)} 個獨特潛力項目")
        print("💯 正在計算詳細評分...")
        
        # 計算詳細評分
        scored_gems = []
        for gem in unique_gems:
            try:
                scores = score_calculator.calculate_comprehensive_score(gem)
                gem['detailed_scores'] = scores
                scored_gems.append(gem)
            except Exception as e:
                logger.error(f"評分計算失敗 {gem.get('name', 'Unknown')}: {e}")
                continue
        
        # 按評分排序
        scored_gems.sort(key=lambda x: x['detailed_scores']['risk_adjusted_score'], reverse=True)
        
        print(f"✅ 評分計算完成，共 {len(scored_gems)} 個項目有效")
        
        # 生成報告
        generate_summary_report(scored_gems)
        
        # 顯示前 5 名詳細報告
        print("\\n🏆 TOP 5 潛力幣詳細分析:")
        print("="*80)
        
        for i, gem in enumerate(scored_gems[:5], 1):
            print(f"\\n【第 {i} 名】")
            print(gem_finder.format_gem_report(gem))
            print(score_calculator.generate_score_report(gem, gem['detailed_scores']))
            print("-"*80)
        
        # 生成投資建議
        generate_investment_suggestions(scored_gems)
        
        print("\\n✨ 分析完成！祝您投資順利！")
        
    except Exception as e:
        logger.error(f"❌ 系統運行錯誤: {e}")
        print(f"❌ 發生錯誤: {e}")
        return 1
    
    return 0

def generate_summary_report(gems: List[Dict]):
    """生成總結報告"""
    print("\\n📈 潛力幣發現總結報告")
    print("="*50)
    
    if not gems:
        print("❌ 未發現符合條件的潛力幣")
        return
    
    # 按推薦等級分類
    recommendations = {}
    for gem in gems:
        rec = gem['detailed_scores']['recommendation']
        if rec not in recommendations:
            recommendations[rec] = []
        recommendations[rec].append(gem)
    
    print(f"📊 總發現項目: {len(gems)} 個")
    print("\\n💡 推薦分布:")
    
    rec_order = ['STRONG_BUY', 'BUY', 'MODERATE_BUY', 'HOLD_WATCH', 'WEAK_HOLD', 'AVOID']
    rec_emojis = {
        'STRONG_BUY': '🔥',
        'BUY': '✅',
        'MODERATE_BUY': '👍',
        'HOLD_WATCH': '👀',
        'WEAK_HOLD': '⚠️',
        'AVOID': '❌'
    }
    
    for rec in rec_order:
        if rec in recommendations:
            count = len(recommendations[rec])
            emoji = rec_emojis.get(rec, '📊')
            print(f"  {emoji} {rec}: {count} 個項目")
    
    # 平均評分
    avg_score = sum(g['detailed_scores']['risk_adjusted_score'] for g in gems) / len(gems)
    print(f"\\n📊 平均評分: {avg_score:.1f}/100")
    
    # 市值分布
    market_caps = [g.get('market_cap', 0) for g in gems if g.get('market_cap', 0) > 0]
    if market_caps:
        avg_mcap = sum(market_caps) / len(market_caps)
        print(f"💰 平均市值: ${avg_mcap:,.0f}")
        print(f"💰 市值範圍: ${min(market_caps):,.0f} - ${max(market_caps):,.0f}")

def generate_investment_suggestions(gems: List[Dict]):
    """生成投資建議"""
    print("\\n💡 投資策略建議")
    print("="*50)
    
    strong_buys = [g for g in gems if g['detailed_scores']['recommendation'] == 'STRONG_BUY']
    buys = [g for g in gems if g['detailed_scores']['recommendation'] == 'BUY']
    moderate_buys = [g for g in gems if g['detailed_scores']['recommendation'] == 'MODERATE_BUY']
    
    if strong_buys:
        print("🔥 強烈推薦 (建議重點關注):")
        for gem in strong_buys[:3]:  # Top 3
            name = gem.get('name', 'Unknown')
            symbol = gem.get('symbol', 'N/A')
            score = gem['detailed_scores']['risk_adjusted_score']
            print(f"   • {name} ({symbol}) - 評分: {score:.1f}")
    
    if buys:
        print("\\n✅ 推薦買入 (適合配置):")
        for gem in buys[:3]:  # Top 3
            name = gem.get('name', 'Unknown')
            symbol = gem.get('symbol', 'N/A')
            score = gem['detailed_scores']['risk_adjusted_score']
            print(f"   • {name} ({symbol}) - 評分: {score:.1f}")
    
    if moderate_buys:
        print("\\n👍 適度買入 (小倉位嘗試):")
        for gem in moderate_buys[:2]:  # Top 2
            name = gem.get('name', 'Unknown')
            symbol = gem.get('symbol', 'N/A')
            score = gem['detailed_scores']['risk_adjusted_score']
            print(f"   • {name} ({symbol}) - 評分: {score:.1f}")
    
    print("\\n⚠️  風險提醒:")
    print("   • 加密貨幣投資有高風險，請勿投入超過承受能力的資金")
    print("   • 建議分散投資，不要將所有資金投入單一項目")
    print("   • 持續關注項目發展，及時調整持倉")
    print("   • 本分析僅供參考，不構成投資建議")

def run_interactive_mode():
    """互動模式運行"""
    print("\\n🎮 進入互動模式")
    print("請選擇操作:")
    print("1. 搜尋趨勢潛力幣")
    print("2. 搜尋新上線潛力幣")
    print("3. 搜尋交易量異常幣")
    print("4. 搜尋社交熱度幣")
    print("5. 全面掃描")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\\n請選擇 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再見!")
                break
            elif choice == '1':
                print("🔍 搜尋趨勢潛力幣中...")
                # 實現趨勢搜尋邏輯
            elif choice == '2':
                print("🔍 搜尋新上線潛力幣中...")
                # 實現新幣搜尋邏輯
            elif choice == '3':
                print("🔍 搜尋交易量異常幣中...")
                # 實現交易量搜尋邏輯
            elif choice == '4':
                print("🔍 搜尋社交熱度幣中...")
                # 實現社交搜尋邏輯
            elif choice == '5':
                print("🚀 執行全面掃描...")
                main()
                break
            else:
                print("❌ 無效選擇，請重新選擇")
                
        except KeyboardInterrupt:
            print("\\n👋 用戶中斷，再見!")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TradeMind 潛力幣發現系統')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='啟動互動模式')
    parser.add_argument('--top', '-t', type=int, default=10,
                       help='顯示前N個結果 (預設: 10)')
    parser.add_argument('--min-score', '-s', type=float, default=0,
                       help='最低評分過濾 (0-100)')
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_mode()
    else:
        exit_code = main()
        sys.exit(exit_code)