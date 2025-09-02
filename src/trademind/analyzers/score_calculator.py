"""
Multi-dimensional scoring system for cryptocurrency analysis
"""
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from ..utils.logger import setup_logger

class GemScoreCalculator:
    """Calculate comprehensive scores for cryptocurrency gems"""
    
    def __init__(self, 
                 social_weight: float = 0.3,
                 onchain_weight: float = 0.25,
                 dev_weight: float = 0.2,
                 liquidity_weight: float = 0.15,
                 holder_weight: float = 0.1):
        
        self.logger = setup_logger(__name__)
        
        # Scoring weights (should sum to 1.0)
        self.social_weight = social_weight
        self.onchain_weight = onchain_weight
        self.dev_weight = dev_weight
        self.liquidity_weight = liquidity_weight
        self.holder_weight = holder_weight
        
        # Validation
        total_weight = sum([social_weight, onchain_weight, dev_weight, 
                           liquidity_weight, holder_weight])
        if abs(total_weight - 1.0) > 0.01:
            self.logger.warning(f"權重總和不等於1.0: {total_weight}")
    
    def calculate_comprehensive_score(self, coin_data: Dict) -> Dict:
        """Calculate comprehensive score across all dimensions"""
        try:
            # Calculate individual dimension scores
            social_score = self.calculate_social_score(coin_data)
            onchain_score = self.calculate_onchain_score(coin_data)
            dev_score = self.calculate_development_score(coin_data)
            liquidity_score = self.calculate_liquidity_score(coin_data)
            holder_score = self.calculate_holder_score(coin_data)
            
            # Calculate weighted total score
            total_score = (
                social_score * self.social_weight +
                onchain_score * self.onchain_weight +
                dev_score * self.dev_weight +
                liquidity_score * self.liquidity_weight +
                holder_score * self.holder_weight
            )
            
            # Calculate momentum and trend scores
            momentum_score = self.calculate_momentum_score(coin_data)
            trend_score = self.calculate_trend_score(coin_data)
            
            # Risk assessment
            risk_score = self.calculate_risk_score(coin_data)
            
            # Final adjusted score (considering risk)
            risk_adjusted_score = total_score * (1 - risk_score / 200)  # Risk reduces score
            
            return {
                'total_score': round(total_score, 2),
                'risk_adjusted_score': round(risk_adjusted_score, 2),
                'dimension_scores': {
                    'social_score': round(social_score, 2),
                    'onchain_score': round(onchain_score, 2),
                    'development_score': round(dev_score, 2),
                    'liquidity_score': round(liquidity_score, 2),
                    'holder_score': round(holder_score, 2)
                },
                'momentum_score': round(momentum_score, 2),
                'trend_score': round(trend_score, 2),
                'risk_score': round(risk_score, 2),
                'grade': self._score_to_grade(risk_adjusted_score),
                'recommendation': self._score_to_recommendation(risk_adjusted_score, risk_score)
            }
            
        except Exception as e:
            self.logger.error(f"綜合評分計算失敗: {e}")
            return self._default_score()
    
    def calculate_social_score(self, coin_data: Dict) -> float:
        """Calculate social media and community score (0-100)"""
        try:
            score = 0.0
            
            # Twitter metrics (40% of social score)
            twitter_followers = coin_data.get('twitter_followers', 0)
            if twitter_followers > 0:
                # Logarithmic scale for followers
                twitter_score = min(40, math.log10(max(twitter_followers, 1)) * 8)
                score += twitter_score
            
            # Reddit metrics (30% of social score)
            reddit_subscribers = coin_data.get('reddit_subscribers', 0)
            reddit_active = coin_data.get('reddit_active_users_48h', 0)
            
            if reddit_subscribers > 0:
                reddit_base_score = min(20, math.log10(max(reddit_subscribers, 1)) * 4)
                score += reddit_base_score
                
                # Activity bonus
                if reddit_active > 0:
                    activity_ratio = reddit_active / reddit_subscribers
                    activity_bonus = min(10, activity_ratio * 200)  # Up to 10 points for activity
                    score += activity_bonus
            
            # Telegram metrics (20% of social score)
            telegram_users = coin_data.get('telegram_users', 0)
            if telegram_users > 0:
                telegram_score = min(20, math.log10(max(telegram_users, 1)) * 4)
                score += telegram_score
            
            # Facebook and other social (10% of social score)
            facebook_likes = coin_data.get('facebook_likes', 0)
            if facebook_likes > 0:
                facebook_score = min(10, math.log10(max(facebook_likes, 1)) * 2)
                score += facebook_score
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"社交媒體評分計算失敗: {e}")
            return 0.0
    
    def calculate_onchain_score(self, coin_data: Dict) -> float:
        """Calculate on-chain metrics score (0-100)"""
        try:
            score = 0.0
            
            # Market cap positioning (30% of onchain score)
            market_cap = coin_data.get('market_cap', 0)
            if market_cap > 0:
                # Sweet spot scoring: 10M-50M gets highest score
                if 10_000_000 <= market_cap <= 50_000_000:
                    score += 30
                elif 5_000_000 <= market_cap < 10_000_000:
                    score += 25
                elif 1_000_000 <= market_cap < 5_000_000:
                    score += 20
                elif 50_000_000 < market_cap <= 100_000_000:
                    score += 15
                else:
                    score += 10
            
            # Volume analysis (25% of onchain score)
            volume_24h = coin_data.get('total_volume', 0)
            if volume_24h > 0 and market_cap > 0:
                volume_ratio = volume_24h / market_cap
                
                if volume_ratio > 0.2:      # Very high turnover
                    score += 25
                elif volume_ratio > 0.1:    # High turnover
                    score += 20
                elif volume_ratio > 0.05:   # Good turnover
                    score += 15
                elif volume_ratio > 0.02:   # Moderate turnover
                    score += 10
                else:                       # Low turnover
                    score += 5
            
            # Price stability vs growth (20% of onchain score)
            price_change_24h = coin_data.get('price_change_percentage_24h', 0)
            price_change_7d = coin_data.get('price_change_percentage_7d', 0)
            
            # Prefer steady growth over extreme volatility
            if 0 <= price_change_7d <= 50:      # Healthy growth
                score += 20
            elif -20 <= price_change_7d < 0:    # Minor correction
                score += 15
            elif 50 < price_change_7d <= 100:   # Strong growth, slightly risky
                score += 10
            else:                               # Too volatile
                score += 5
            
            # Supply metrics (15% of onchain score)
            circulating_supply = coin_data.get('circulating_supply', 0)
            total_supply = coin_data.get('total_supply', 0)
            max_supply = coin_data.get('max_supply', 0)
            
            if circulating_supply > 0 and total_supply > 0:
                circulation_ratio = circulating_supply / total_supply
                
                if circulation_ratio > 0.8:     # Most tokens in circulation
                    score += 15
                elif circulation_ratio > 0.5:   # Good circulation
                    score += 10
                else:                          # Low circulation (could be good or bad)
                    score += 5
            
            # All-time high analysis (10% of onchain score)
            current_price = coin_data.get('current_price', 0)
            ath = coin_data.get('ath', 0)
            
            if current_price > 0 and ath > 0:
                ath_distance = (ath - current_price) / ath
                
                if ath_distance < 0.2:          # Close to ATH
                    score += 5  # Risky but could breakout
                elif 0.2 <= ath_distance < 0.5:  # Reasonable distance
                    score += 10
                elif 0.5 <= ath_distance < 0.8:  # Good recovery potential
                    score += 8
                else:                           # Far from ATH
                    score += 5
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"鏈上數據評分計算失敗: {e}")
            return 0.0
    
    def calculate_development_score(self, coin_data: Dict) -> float:
        """Calculate development activity score (0-100)"""
        try:
            score = 0.0
            
            # GitHub commits (40% of dev score)
            commits_4w = coin_data.get('github_commits_4w', 0)
            if commits_4w > 0:
                if commits_4w >= 100:       # Very active development
                    score += 40
                elif commits_4w >= 50:      # Active development
                    score += 30
                elif commits_4w >= 20:      # Moderate development
                    score += 20
                elif commits_4w >= 5:       # Some development
                    score += 10
                else:                       # Minimal development
                    score += 5
            
            # GitHub stars (20% of dev score)
            stars = coin_data.get('github_stars', 0)
            if stars > 0:
                # Logarithmic scale for stars
                stars_score = min(20, math.log10(max(stars, 1)) * 5)
                score += stars_score
            
            # GitHub forks (15% of dev score)
            forks = coin_data.get('github_forks', 0)
            if forks > 0:
                forks_score = min(15, math.log10(max(forks, 1)) * 3.75)
                score += forks_score
            
            # Issue resolution (15% of dev score)
            closed_issues = coin_data.get('github_issues', 0)
            if closed_issues > 0:
                if closed_issues >= 100:    # Good issue management
                    score += 15
                elif closed_issues >= 50:   # Decent issue management
                    score += 10
                elif closed_issues >= 20:   # Some issue management
                    score += 7
                else:                       # Limited issue management
                    score += 3
            
            # Pull requests (10% of dev score)
            pull_requests = coin_data.get('github_pull_requests', 0)
            if pull_requests > 0:
                if pull_requests >= 50:     # Very collaborative
                    score += 10
                elif pull_requests >= 20:   # Collaborative
                    score += 7
                elif pull_requests >= 10:   # Some collaboration
                    score += 5
                else:                       # Limited collaboration
                    score += 2
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"開發活躍度評分計算失敗: {e}")
            return 0.0
    
    def calculate_liquidity_score(self, coin_data: Dict) -> float:
        """Calculate liquidity and trading quality score (0-100)"""
        try:
            score = 0.0
            
            market_cap = coin_data.get('market_cap', 0)
            volume_24h = coin_data.get('total_volume', 0)
            
            if market_cap <= 0 or volume_24h <= 0:
                return 0.0
            
            # Volume to market cap ratio (50% of liquidity score)
            volume_ratio = volume_24h / market_cap
            
            if volume_ratio >= 0.3:         # Extremely high liquidity
                score += 50
            elif volume_ratio >= 0.2:       # Very high liquidity
                score += 45
            elif volume_ratio >= 0.1:       # High liquidity
                score += 40
            elif volume_ratio >= 0.05:      # Good liquidity
                score += 30
            elif volume_ratio >= 0.02:      # Moderate liquidity
                score += 20
            elif volume_ratio >= 0.01:      # Low liquidity
                score += 10
            else:                           # Very low liquidity
                score += 5
            
            # Absolute volume threshold (25% of liquidity score)
            if volume_24h >= 10_000_000:    # Very high absolute volume
                score += 25
            elif volume_24h >= 5_000_000:   # High absolute volume
                score += 20
            elif volume_24h >= 1_000_000:   # Good absolute volume
                score += 15
            elif volume_24h >= 500_000:     # Moderate absolute volume
                score += 10
            elif volume_24h >= 100_000:     # Low absolute volume
                score += 5
            else:                           # Very low absolute volume
                score += 2
            
            # Price spread analysis (would need order book data - approximate using volatility)
            # High 24h vs Low 24h spread (25% of liquidity score)
            high_24h = coin_data.get('high_24h', 0)
            low_24h = coin_data.get('low_24h', 0)
            current_price = coin_data.get('current_price', 0)
            
            if high_24h > 0 and low_24h > 0 and current_price > 0:
                spread = (high_24h - low_24h) / current_price
                
                if spread <= 0.05:          # Very tight spread
                    score += 25
                elif spread <= 0.1:         # Good spread
                    score += 20
                elif spread <= 0.2:         # Moderate spread
                    score += 15
                elif spread <= 0.3:         # Wide spread
                    score += 10
                else:                       # Very wide spread
                    score += 5
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"流動性評分計算失敗: {e}")
            return 0.0
    
    def calculate_holder_score(self, coin_data: Dict) -> float:
        """Calculate holder quality and distribution score (0-100)"""
        # Note: CoinGecko doesn't provide detailed holder data
        # This is a placeholder for future integration with blockchain analysis
        try:
            score = 50.0  # Default medium score
            
            # We can infer some holder quality from available data
            market_cap = coin_data.get('market_cap', 0)
            volume_24h = coin_data.get('total_volume', 0)
            
            if market_cap > 0 and volume_24h > 0:
                # Lower volume/market cap might indicate stronger hands
                hodl_ratio = 1 - min(volume_24h / market_cap, 1)
                
                if hodl_ratio > 0.8:        # Very strong hands
                    score = 80
                elif hodl_ratio > 0.6:      # Strong hands
                    score = 70
                elif hodl_ratio > 0.4:      # Moderate hands
                    score = 60
                elif hodl_ratio > 0.2:      # Weak hands
                    score = 40
                else:                       # Very weak hands
                    score = 20
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"持有者評分計算失敗: {e}")
            return 50.0
    
    def calculate_momentum_score(self, coin_data: Dict) -> float:
        """Calculate price momentum score (0-100)"""
        try:
            score = 50.0  # Neutral starting point
            
            # Short term momentum (24h) - 40% weight
            change_24h = coin_data.get('price_change_percentage_24h', 0)
            if change_24h > 10:
                score += 20
            elif change_24h > 5:
                score += 15
            elif change_24h > 0:
                score += 10
            elif change_24h > -5:
                score -= 5
            elif change_24h > -10:
                score -= 10
            else:
                score -= 20
            
            # Medium term momentum (7d) - 60% weight  
            change_7d = coin_data.get('price_change_percentage_7d', 0)
            if change_7d > 50:
                score += 30
            elif change_7d > 20:
                score += 25
            elif change_7d > 10:
                score += 20
            elif change_7d > 0:
                score += 15
            elif change_7d > -10:
                score -= 10
            elif change_7d > -20:
                score -= 15
            else:
                score -= 25
            
            return max(0, min(score, 100))
            
        except Exception as e:
            self.logger.error(f"動量評分計算失敗: {e}")
            return 50.0
    
    def calculate_trend_score(self, coin_data: Dict) -> float:
        """Calculate long-term trend score (0-100)"""
        try:
            score = 50.0  # Neutral starting point
            
            # Long term trend (30d if available)
            change_30d = coin_data.get('price_change_percentage_30d', 0)
            if change_30d:
                if change_30d > 100:
                    score += 30
                elif change_30d > 50:
                    score += 25
                elif change_30d > 20:
                    score += 20
                elif change_30d > 0:
                    score += 15
                else:
                    score -= abs(change_30d) / 10  # Penalize downtrend
            
            # ATH analysis for trend
            current_price = coin_data.get('current_price', 0)
            ath = coin_data.get('ath', 0)
            
            if current_price > 0 and ath > 0:
                ath_ratio = current_price / ath
                
                if ath_ratio > 0.8:         # Near ATH - strong trend
                    score += 20
                elif ath_ratio > 0.5:       # Good recovery
                    score += 15
                elif ath_ratio > 0.2:       # Moderate recovery
                    score += 10
                else:                       # Far from ATH
                    score += 5
            
            return max(0, min(score, 100))
            
        except Exception as e:
            self.logger.error(f"趨勢評分計算失敗: {e}")
            return 50.0
    
    def calculate_risk_score(self, coin_data: Dict) -> float:
        """Calculate risk score (0-100, higher = more risky)"""
        try:
            risk = 0.0
            
            # Market cap risk
            market_cap = coin_data.get('market_cap', 0)
            if market_cap < 1_000_000:      # Very small market cap
                risk += 30
            elif market_cap < 10_000_000:   # Small market cap
                risk += 20
            elif market_cap < 50_000_000:   # Medium market cap
                risk += 10
            # Large market caps get 0 additional risk
            
            # Volatility risk
            change_7d = abs(coin_data.get('price_change_percentage_7d', 0))
            if change_7d > 100:             # Extreme volatility
                risk += 25
            elif change_7d > 50:            # High volatility
                risk += 15
            elif change_7d > 20:            # Moderate volatility
                risk += 10
            
            # Liquidity risk
            volume_24h = coin_data.get('total_volume', 0)
            if volume_24h < 100_000:        # Very low volume
                risk += 20
            elif volume_24h < 500_000:      # Low volume
                risk += 15
            elif volume_24h < 1_000_000:    # Moderate volume
                risk += 10
            
            # Social presence risk (no community = higher risk)
            twitter = coin_data.get('twitter_followers', 0)
            reddit = coin_data.get('reddit_subscribers', 0)
            
            if twitter < 1000 and reddit < 1000:  # No social presence
                risk += 15
            elif twitter < 5000 and reddit < 5000:  # Weak social presence
                risk += 10
            
            # Development risk
            commits = coin_data.get('github_commits_4w', 0)
            if commits == 0:                # No recent development
                risk += 10
            elif commits < 5:               # Minimal development
                risk += 5
            
            return min(risk, 100)
            
        except Exception as e:
            self.logger.error(f"風險評分計算失敗: {e}")
            return 50.0
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _score_to_recommendation(self, score: float, risk_score: float) -> str:
        """Convert score and risk to investment recommendation"""
        if score >= 85 and risk_score <= 30:
            return 'STRONG_BUY'
        elif score >= 75 and risk_score <= 40:
            return 'BUY'
        elif score >= 65 and risk_score <= 50:
            return 'MODERATE_BUY'
        elif score >= 55:
            return 'HOLD_WATCH'
        elif score >= 45:
            return 'WEAK_HOLD'
        else:
            return 'AVOID'
    
    def _default_score(self) -> Dict:
        """Return default score structure when calculation fails"""
        return {
            'total_score': 0.0,
            'risk_adjusted_score': 0.0,
            'dimension_scores': {
                'social_score': 0.0,
                'onchain_score': 0.0,
                'development_score': 0.0,
                'liquidity_score': 0.0,
                'holder_score': 0.0
            },
            'momentum_score': 0.0,
            'trend_score': 0.0,
            'risk_score': 100.0,
            'grade': 'F',
            'recommendation': 'AVOID'
        }
    
    def generate_score_report(self, coin_data: Dict, scores: Dict) -> str:
        """Generate a detailed scoring report"""
        try:
            name = coin_data.get('name', 'Unknown')
            symbol = coin_data.get('symbol', 'N/A')
            
            report = f"""
📊 {name} ({symbol}) 評分報告
═══════════════════════════════════════

🎯 總體評分: {scores['risk_adjusted_score']:.1f}/100 (等級: {scores['grade']})
💡 投資建議: {scores['recommendation']}

📈 分項評分:
├─ 社交媒體: {scores['dimension_scores']['social_score']:.1f}/100
├─ 鏈上數據: {scores['dimension_scores']['onchain_score']:.1f}/100  
├─ 開發活躍: {scores['dimension_scores']['development_score']:.1f}/100
├─ 流動性: {scores['dimension_scores']['liquidity_score']:.1f}/100
└─ 持有者: {scores['dimension_scores']['holder_score']:.1f}/100

🚀 動量分析:
├─ 價格動量: {scores['momentum_score']:.1f}/100
└─ 長期趨勢: {scores['trend_score']:.1f}/100

⚠️  風險評估: {scores['risk_score']:.1f}/100

═══════════════════════════════════════
"""
            return report
            
        except Exception as e:
            self.logger.error(f"評分報告生成失敗: {e}")
            return f"無法生成 {coin_data.get('name', 'Unknown')} 的評分報告"