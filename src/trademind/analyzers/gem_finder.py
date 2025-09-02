"""
Gem (potential) coin discovery system
"""
import asyncio
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from ..collectors.coingecko import CoinGeckoClient
from ..utils.logger import setup_logger

class GemFinder:
    """Discover potential gem coins using various strategies"""
    
    def __init__(self, 
                 min_market_cap: int = 1_000_000,
                 max_market_cap: int = 100_000_000,
                 min_volume_24h: int = 100_000,
                 min_holders: int = 1000,
                 max_age_days: int = 90,
                 min_age_days: int = 7):
        
        self.coingecko = CoinGeckoClient()
        self.logger = setup_logger(__name__)
        
        # Filtering criteria
        self.min_market_cap = min_market_cap
        self.max_market_cap = max_market_cap
        self.min_volume_24h = min_volume_24h
        self.min_holders = min_holders
        self.max_age_days = max_age_days
        self.min_age_days = min_age_days
        
        # Track processed coins to avoid duplicates
        self.processed_coins: Set[str] = set()
        
    def find_trending_gems(self) -> List[Dict]:
        """Find gems from trending coins"""
        self.logger.info("🔍 搜尋趨勢潛力幣...")
        
        trending_coins = self.coingecko.get_trending_coins()
        if not trending_coins:
            self.logger.warning("無法獲取趨勢幣數據")
            return []
        
        gem_candidates = []
        for coin in trending_coins:
            try:
                # Get detailed data for analysis
                details = self.coingecko.get_coin_details(coin['id'])
                if details and self._is_gem_candidate(details):
                    gem_data = self._enrich_gem_data(details, source='trending')
                    gem_candidates.append(gem_data)
                    
            except Exception as e:
                self.logger.error(f"獲取 {coin['id']} 詳細資訊失敗: {e}")
                continue
        
        self.logger.info(f"從趨勢幣中發現 {len(gem_candidates)} 個潛力項目")
        return gem_candidates
    
    def find_new_listings(self) -> List[Dict]:
        """Find gems from recently listed coins"""
        self.logger.info("🔍 搜尋新上線潛力幣...")
        
        # Get recently listed coins (approximation)
        new_coins = self.coingecko.get_new_coins(days=30)
        if not new_coins:
            self.logger.warning("無法獲取新幣數據")
            return []
        
        gem_candidates = []
        for coin in new_coins:
            if coin['id'] in self.processed_coins:
                continue
                
            try:
                # Get detailed data for proper analysis
                details = self.coingecko.get_coin_details(coin['id'])
                if details and self._is_gem_candidate(details):
                    gem_data = self._enrich_gem_data(details, source='new_listing')
                    gem_candidates.append(gem_data)
                    self.processed_coins.add(coin['id'])
                    
            except Exception as e:
                self.logger.error(f"分析新幣 {coin['id']} 失敗: {e}")
                continue
        
        self.logger.info(f"從新上線幣中發現 {len(gem_candidates)} 個潛力項目")
        return gem_candidates
    
    def find_volume_surge_gems(self) -> List[Dict]:
        """Find gems with unusual volume activity"""
        self.logger.info("🔍 搜尋交易量異常潛力幣...")
        
        # Get coins with high volume but smaller market cap
        market_data = self.coingecko._make_sync_request("coins/markets", {
            'vs_currency': 'usd',
            'order': 'volume_desc',  # Sort by volume
            'per_page': 250,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h,7d'
        })
        
        if not market_data:
            return []
        
        gem_candidates = []
        for coin in market_data:
            if coin['id'] in self.processed_coins:
                continue
                
            # Check if it's a small/mid cap with high volume (potential gem)
            market_cap = coin.get('market_cap', 0)
            volume = coin.get('total_volume', 0)
            
            if (self.min_market_cap <= market_cap <= self.max_market_cap and 
                volume >= self.min_volume_24h):
                
                try:
                    details = self.coingecko.get_coin_details(coin['id'])
                    if details and self._is_gem_candidate(details):
                        gem_data = self._enrich_gem_data(details, source='volume_surge')
                        gem_candidates.append(gem_data)
                        self.processed_coins.add(coin['id'])
                        
                except Exception as e:
                    self.logger.error(f"分析交易量異常幣 {coin['id']} 失敗: {e}")
                    continue
        
        self.logger.info(f"從交易量異常中發現 {len(gem_candidates)} 個潛力項目")
        return gem_candidates
    
    def find_social_buzz_gems(self) -> List[Dict]:
        """Find gems with growing social media presence"""
        self.logger.info("🔍 搜尋社交媒體熱度潛力幣...")
        
        # This would require integration with social media APIs
        # For now, we'll use CoinGecko's social data from detailed coin info
        
        # Get a broader list of coins to analyze their social metrics
        market_data = self.coingecko._make_sync_request("coins/markets", {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': 'false'
        })
        
        if not market_data:
            return []
        
        gem_candidates = []
        for coin in market_data[:50]:  # Limit to top 50 to avoid rate limits
            if coin['id'] in self.processed_coins:
                continue
                
            market_cap = coin.get('market_cap', 0)
            if self.min_market_cap <= market_cap <= self.max_market_cap:
                try:
                    details = self.coingecko.get_coin_details(coin['id'])
                    if details and self._has_social_buzz(details) and self._is_gem_candidate(details):
                        gem_data = self._enrich_gem_data(details, source='social_buzz')
                        gem_candidates.append(gem_data)
                        self.processed_coins.add(coin['id'])
                        
                except Exception as e:
                    self.logger.error(f"分析社交熱度幣 {coin['id']} 失敗: {e}")
                    continue
        
        self.logger.info(f"從社交媒體熱度中發現 {len(gem_candidates)} 個潛力項目")
        return gem_candidates
    
    def comprehensive_scan(self) -> List[Dict]:
        """Run a comprehensive scan using all discovery methods"""
        self.logger.info("🚀 開始全面潛力幣掃描...")
        
        all_gems = []
        
        # Clear processed coins for fresh scan
        self.processed_coins.clear()
        
        # Run all discovery methods
        all_gems.extend(self.find_trending_gems())
        all_gems.extend(self.find_new_listings())
        all_gems.extend(self.find_volume_surge_gems())
        all_gems.extend(self.find_social_buzz_gems())
        
        # Remove duplicates and sort by potential score
        unique_gems = self._deduplicate_gems(all_gems)
        sorted_gems = sorted(unique_gems, key=lambda x: x.get('potential_score', 0), reverse=True)
        
        self.logger.info(f"總共發現 {len(sorted_gems)} 個獨特潛力項目")
        return sorted_gems
    
    def _is_gem_candidate(self, coin: Dict) -> bool:
        """Check if a coin meets basic gem criteria"""
        try:
            market_cap = coin.get('market_cap', 0)
            volume_24h = coin.get('total_volume', 0)
            
            # Basic filters
            if not (self.min_market_cap <= market_cap <= self.max_market_cap):
                return False
                
            if volume_24h < self.min_volume_24h:
                return False
            
            # Check if it has reasonable liquidity (volume/market_cap ratio)
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio < 0.01:  # Less than 1% daily turnover is too low
                    return False
            
            # Avoid coins with no social presence at all
            twitter_followers = coin.get('twitter_followers', 0)
            reddit_subscribers = coin.get('reddit_subscribers', 0)
            
            if twitter_followers == 0 and reddit_subscribers == 0:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"篩選檢查失敗: {e}")
            return False
    
    def _has_social_buzz(self, coin: Dict) -> bool:
        """Check if coin has growing social media presence"""
        try:
            twitter_followers = coin.get('twitter_followers', 0)
            reddit_subscribers = coin.get('reddit_subscribers', 0)
            reddit_active = coin.get('reddit_active_users_48h', 0)
            telegram_users = coin.get('telegram_users', 0)
            
            # Consider it buzzing if it has decent social numbers
            social_score = 0
            
            if twitter_followers > 10000:
                social_score += 1
            if reddit_subscribers > 5000:
                social_score += 1
            if reddit_active > 100:
                social_score += 1
            if telegram_users > 1000:
                social_score += 1
                
            return social_score >= 2  # At least 2 out of 4 criteria
            
        except Exception:
            return False
    
    def _enrich_gem_data(self, coin: Dict, source: str = 'unknown') -> Dict:
        """Enrich coin data with additional analysis"""
        try:
            # Calculate basic potential score
            potential_score = self._calculate_potential_score(coin)
            
            # Add discovery metadata
            enriched = coin.copy()
            enriched.update({
                'discovery_source': source,
                'discovery_date': datetime.now().isoformat(),
                'potential_score': potential_score,
                'risk_level': self._assess_risk_level(coin),
                'recommendation': self._generate_recommendation(coin, potential_score)
            })
            
            return enriched
            
        except Exception as e:
            self.logger.error(f"數據豐富化失敗: {e}")
            return coin
    
    def _calculate_potential_score(self, coin: Dict) -> float:
        """Calculate a potential score for the gem (0-100)"""
        try:
            score = 0.0
            
            # Market cap score (sweet spot gets higher score)
            market_cap = coin.get('market_cap', 0)
            if 5_000_000 <= market_cap <= 50_000_000:  # Sweet spot
                score += 25
            elif 1_000_000 <= market_cap < 5_000_000:   # Small but not too small
                score += 20
            elif market_cap < 1_000_000:                # Too small, risky
                score += 10
            
            # Volume/Market cap ratio (liquidity)
            volume = coin.get('total_volume', 0)
            if market_cap > 0:
                volume_ratio = volume / market_cap
                if volume_ratio > 0.1:      # Very active
                    score += 20
                elif volume_ratio > 0.05:   # Active
                    score += 15
                elif volume_ratio > 0.02:   # Moderate
                    score += 10
            
            # Social presence
            twitter = coin.get('twitter_followers', 0)
            reddit = coin.get('reddit_subscribers', 0)
            
            if twitter > 50000 or reddit > 20000:
                score += 15
            elif twitter > 10000 or reddit > 5000:
                score += 10
            elif twitter > 1000 or reddit > 1000:
                score += 5
            
            # Development activity
            commits = coin.get('github_commits_4w', 0)
            stars = coin.get('github_stars', 0)
            
            if commits > 50:
                score += 15
            elif commits > 20:
                score += 10
            elif commits > 5:
                score += 5
                
            if stars > 1000:
                score += 5
            elif stars > 100:
                score += 3
            
            # Price performance (recent gains can indicate momentum)
            price_change_7d = coin.get('price_change_percentage_7d', 0)
            if 0 < price_change_7d < 100:  # Positive but not crazy pump
                score += 10
            elif price_change_7d > 100:    # Might be too late
                score += 5
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            self.logger.error(f"評分計算失敗: {e}")
            return 0.0
    
    def _assess_risk_level(self, coin: Dict) -> str:
        """Assess risk level of the gem"""
        try:
            risk_factors = 0
            
            # Market cap too small
            market_cap = coin.get('market_cap', 0)
            if market_cap < 5_000_000:
                risk_factors += 1
            
            # Low volume
            volume = coin.get('total_volume', 0)
            if volume < 500_000:
                risk_factors += 1
            
            # No social presence
            twitter = coin.get('twitter_followers', 0)
            reddit = coin.get('reddit_subscribers', 0)
            if twitter < 1000 and reddit < 1000:
                risk_factors += 1
            
            # No development activity
            commits = coin.get('github_commits_4w', 0)
            if commits == 0:
                risk_factors += 1
            
            # Recent massive pump (might be dump incoming)
            price_change_7d = coin.get('price_change_percentage_7d', 0)
            if price_change_7d > 200:
                risk_factors += 1
            
            if risk_factors >= 4:
                return 'VERY_HIGH'
            elif risk_factors >= 3:
                return 'HIGH'
            elif risk_factors >= 2:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except Exception:
            return 'UNKNOWN'
    
    def _generate_recommendation(self, coin: Dict, potential_score: float) -> str:
        """Generate investment recommendation"""
        try:
            if potential_score >= 75:
                return 'STRONG_BUY'
            elif potential_score >= 60:
                return 'BUY'
            elif potential_score >= 40:
                return 'WATCH'
            else:
                return 'PASS'
        except Exception:
            return 'UNKNOWN'
    
    def _deduplicate_gems(self, gems: List[Dict]) -> List[Dict]:
        """Remove duplicate gems and keep the best version"""
        seen_ids = {}
        unique_gems = []
        
        for gem in gems:
            gem_id = gem.get('id')
            if gem_id not in seen_ids:
                seen_ids[gem_id] = gem
                unique_gems.append(gem)
            else:
                # Keep the one with higher potential score
                existing = seen_ids[gem_id]
                if gem.get('potential_score', 0) > existing.get('potential_score', 0):
                    # Remove the existing one and add the new one
                    unique_gems = [g for g in unique_gems if g.get('id') != gem_id]
                    unique_gems.append(gem)
                    seen_ids[gem_id] = gem
        
        return unique_gems
    
    def format_gem_report(self, gem: Dict) -> str:
        """Format gem data into a readable report"""
        try:
            name = gem.get('name', 'Unknown')
            symbol = gem.get('symbol', 'N/A')
            market_cap = gem.get('market_cap', 0)
            volume = gem.get('total_volume', 0)
            price = gem.get('current_price', 0)
            potential_score = gem.get('potential_score', 0)
            risk_level = gem.get('risk_level', 'UNKNOWN')
            recommendation = gem.get('recommendation', 'UNKNOWN')
            source = gem.get('discovery_source', 'unknown')
            
            # Price changes
            change_24h = gem.get('price_change_percentage_24h', 0)
            change_7d = gem.get('price_change_percentage_7d', 0)
            
            # Social metrics
            twitter = gem.get('twitter_followers', 0)
            reddit = gem.get('reddit_subscribers', 0)
            
            report = f"""
💎 {name} (${symbol})
───────────────────────────
💰 價格: ${price:.6f}
📊 市值: ${market_cap:,.0f}
📈 24h 交易量: ${volume:,.0f}
🔥 潛力評分: {potential_score:.1f}/100

📈 價格變化:
   24h: {change_24h:+.2f}%
   7d:  {change_7d:+.2f}%

🌐 社交媒體:
   Twitter: {twitter:,} 關注者
   Reddit: {reddit:,} 訂閱者

⚠️ 風險等級: {risk_level}
💡 建議: {recommendation}
🔍 發現來源: {source}

─────────────────────────────
"""
            return report
            
        except Exception as e:
            self.logger.error(f"報告格式化失敗: {e}")
            return f"無法格式化 {gem.get('name', 'Unknown')} 的報告"