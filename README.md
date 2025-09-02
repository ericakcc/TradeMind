# TradeMind 🐋

基於鏈上數據的異常偵測與鯨魚追蹤系統 - 從 BSC 開始學習區塊鏈監控

## 📋 專案概述

TradeMind 是一個專門監控鏈上數據異常的系統，特別專注於：
- 🐋 鯨魚（大額）交易監控
- 📊 交易所資金流向追蹤  
- 🔍 異常交易模式識別
- 📈 價格影響分析

### 當前功能（Phase 1 - 已完成）
- BSC 鯨魚交易監控
- USDT 大額轉帳追蹤
- 交易所地址識別
- 實時警報系統

### 🆕 全新功能（Phase 2 - 潛力幣發現系統）
- 🔍 **智能潛力幣發現**: 多策略挖掘有潛力的低市值項目
- 📊 **多維度評分系統**: 社交、鏈上、開發、流動性全面評估
- 🎯 **精準篩選條件**: 可自定義市值、交易量、年齡等條件
- 📈 **風險評估模型**: 智能評估投資風險等級
- 📋 **專業分析報告**: 詳細的項目分析和投資建議

## 🚀 快速開始

### 1. 環境設置

```bash
# 克隆專案
git clone <your-repo>
cd TradeMind

# 使用 uv 安裝依賴
uv sync

# 複製配置文件
cp config/.env.example .env
```

### 2. 配置 API Key

編輯 `.env` 文件，加入你的 BSCScan API Key：

```bash
BSCSCAN_API_KEY=your_api_key_here
```

> 💡 在 [BSCScan](https://bscscan.com/apis) 免費申請 API Key

### 3. 運行測試

```bash
# 運行系統測試
uv run python scripts/quick_test.py

# 🆕 運行潛力幣發現系統
uv run python scripts/gem_discovery_demo.py

# 鯨魚監控（原功能）
uv run python scripts/quick_start.py
```

## 📁 專案結構

```
TradeMind/
├── .claude/tasks/          # 開發任務追蹤
├── src/trademind/          # 核心程式碼
│   ├── collectors/         # 數據收集器
│   │   ├── bscscan.py      # BSC API 客戶端
│   │   └── coingecko.py    # 🆕 CoinGecko API 客戶端
│   ├── analyzers/          # 🆕 分析模組
│   │   ├── gem_finder.py   # 🆕 潛力幣發現器
│   │   └── score_calculator.py # 🆕 多維度評分系統
│   ├── monitors/           # 監控模組  
│   │   └── whale_tracker.py # 鯨魚追蹤器
│   └── utils/              # 工具函數
├── config/                 # 配置文件
│   ├── settings.py         # 配置管理（已擴展）
│   └── .env.example        # 環境變數範本
├── docs/                   # 🆕 文檔
│   ├── 專案教學文檔.md      # 完整教學文檔
│   └── 潛力幣發現系統使用指南.md # 🆕 使用指南
├── data/                   # 數據存儲
├── logs/                   # 日誌文件
├── scripts/                # 執行腳本
│   ├── quick_start.py      # 鯨魚監控腳本
│   ├── quick_test.py       # 🆕 系統測試腳本
│   └── gem_discovery_demo.py # 🆕 潛力幣發現演示
└── README.md              # 專案說明
```

## 🔧 主要模組

### 原有模組
#### BSCScanClient
- BSC 區塊鏈數據收集
- API 速率限制管理
- 異步和同步接口

#### WhaleTracker  
- 大額交易識別
- 交易所資金流向分析
- 風險等級評估

### 🆕 新增模組
#### CoinGeckoClient
- CoinGecko API 整合
- 市場數據、社交數據、開發數據收集
- 趨勢幣和新幣發現

#### GemFinder
- 多策略潛力幣發現
- 智能篩選和分類
- 可自定義發現條件

#### GemScoreCalculator
- 多維度綜合評分（社交、鏈上、開發、流動性、持有者）
- 風險評估和調整
- 投資建議生成

## 📊 使用示例

### 鯨魚監控（原功能）
```python
from src.trademind.monitors.whale_tracker import WhaleTracker
from config.settings import config

# 初始化追蹤器
tracker = WhaleTracker(
    api_key=config.BSCSCAN_API_KEY,
    whale_threshold_usd=100000  # 10萬美元門檻
)

# 掃描 USDT 鯨魚交易
whale_txs = tracker.scan_recent_transactions_sync(
    contract_address=config.BSC_USDT_CONTRACT,
    token_price_usd=1.0
)

for tx in whale_txs:
    print(tracker.format_whale_alert(tx))
```

### 🆕 潛力幣發現
```python
from src.trademind.analyzers.gem_finder import GemFinder
from src.trademind.analyzers.score_calculator import GemScoreCalculator

# 初始化潛力幣發現器
finder = GemFinder(
    min_market_cap=1_000_000,      # 最小市值 100 萬美元
    max_market_cap=50_000_000,     # 最大市值 5000 萬美元
    min_volume_24h=100_000         # 最小日交易量 10 萬美元
)

# 初始化評分計算器
calculator = GemScoreCalculator()

# 全面掃描潛力幣
gems = finder.comprehensive_scan()

# 計算詳細評分
for gem in gems:
    scores = calculator.calculate_comprehensive_score(gem)
    
    print(f"💎 {gem['name']} ({gem['symbol']})")
    print(f"📊 評分: {scores['risk_adjusted_score']:.1f}/100")
    print(f"💡 建議: {scores['recommendation']}")
    print(f"⚠️  風險: {scores['risk_score']:.1f}/100")
    print("-" * 50)
```

## ⚙️ 配置說明

### 鯨魚監控配置
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `WHALE_THRESHOLD_USD` | 鯨魚交易金額門檻 | 100,000 |
| `CHECK_INTERVAL_SECONDS` | 檢查間隔 | 60 |
| `MAX_API_CALLS_PER_SECOND` | API 調用限制 | 4 |

### 🆕 潛力幣發現配置
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `GEM_MIN_MARKET_CAP` | 最小市值門檻 | 1,000,000 |
| `GEM_MAX_MARKET_CAP` | 最大市值門檻 | 100,000,000 |
| `GEM_MIN_VOLUME_24H` | 最小24h交易量 | 100,000 |
| `GEM_MIN_HOLDERS` | 最小持有者數量 | 1,000 |
| `GEM_MAX_AGE_DAYS` | 最大項目年齡（天） | 90 |
| `GEM_MIN_AGE_DAYS` | 最小項目年齡（天） | 7 |

### 🆕 評分權重配置
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `SOCIAL_SCORE_WEIGHT` | 社交媒體評分權重 | 0.3 |
| `ONCHAIN_SCORE_WEIGHT` | 鏈上數據評分權重 | 0.25 |
| `DEV_SCORE_WEIGHT` | 開發活躍度評分權重 | 0.2 |
| `LIQUIDITY_SCORE_WEIGHT` | 流動性評分權重 | 0.15 |
| `HOLDER_SCORE_WEIGHT` | 持有者評分權重 | 0.1 |

## 📈 開發路線圖

### ✅ Phase 1 - BSC 基礎監控（已完成）
- [x] 專案架構建立
- [x] BSCScan API 整合
- [x] 鯨魚交易識別  
- [ ] Telegram 警報
- [ ] SQLite 數據存儲

### ✅ Phase 2 - 潛力幣發現系統（已完成）
- [x] CoinGecko API 整合
- [x] 多策略潛力幣發現
- [x] 多維度評分系統
- [x] 風險評估模型
- [x] 專業分析報告
- [x] 完整使用文檔

### 🔄 Phase 3 - 功能增強（進行中）
- [ ] DEX 流動性監控
- [ ] 以太坊支援
- [ ] Telegram 警報系統
- [ ] SQLite 數據存儲
- [ ] Web 儀表板

### 🔮 Phase 4 - 進階功能（未來）
- [ ] 機器學習異常檢測
- [ ] 多鏈監控
- [ ] 自動交易信號
- [ ] 容器化部署
- [ ] 實時數據流處理
- [ ] 移動應用程式

## 🛠️ 開發環境

- **Python**: 3.11+
- **套件管理**: uv
- **API**: BSCScan
- **資料庫**: SQLite (後期 PostgreSQL)

## 📋 任務追蹤

開發進度請查看：`.claude/tasks/README.md`

## ⚠️ 風險聲明

此專案僅供學習和研究用途：
- 不提供投資建議
- 鏈上數據可能延遲或不準確
- 請自行承擔使用風險

## 📄 授權

MIT License

---

**💡 提示**: 如果是第一次使用鏈上監控，建議先從理解 BSC 的基本交易開始！