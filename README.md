# TradeMind 🐋

基於鏈上數據的異常偵測與鯨魚追蹤系統 - 從 BSC 開始學習區塊鏈監控

## 📋 專案概述

TradeMind 是一個專門監控鏈上數據異常的系統，特別專注於：
- 🐋 鯨魚（大額）交易監控
- 📊 交易所資金流向追蹤  
- 🔍 異常交易模式識別
- 📈 價格影響分析

### 當前功能（Phase 1）
- BSC 鯨魚交易監控
- USDT 大額轉帳追蹤
- 交易所地址識別
- 實時警報系統

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
# 使用 uv 運行快速測試
uv run python scripts/quick_start.py
```

## 📁 專案結構

```
TradeMind/
├── .claude/tasks/          # 開發任務追蹤
├── src/trademind/          # 核心程式碼
│   ├── collectors/         # 數據收集器
│   ├── monitors/           # 監控模組  
│   ├── detectors/          # 異常偵測
│   └── utils/              # 工具函數
├── config/                 # 配置文件
│   ├── settings.py         # 配置管理
│   └── .env.example        # 環境變數範本
├── data/                   # 數據存儲
├── logs/                   # 日誌文件
├── scripts/                # 執行腳本
└── README.md              # 專案說明
```

## 🔧 主要模組

### BSCScanClient
- BSC 區塊鏈數據收集
- API 速率限制管理
- 異步和同步接口

### WhaleTracker  
- 大額交易識別
- 交易所資金流向分析
- 風險等級評估

## 📊 監控示例

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

## ⚙️ 配置說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `WHALE_THRESHOLD_USD` | 鯨魚交易金額門檻 | 100,000 |
| `CHECK_INTERVAL_SECONDS` | 檢查間隔 | 60 |
| `MAX_API_CALLS_PER_SECOND` | API 調用限制 | 4 |

## 📈 開發路線圖

### ✅ Phase 1 - BSC 基礎監控
- [x] 專案架構建立
- [x] BSCScan API 整合
- [x] 鯨魚交易識別  
- [ ] Telegram 警報
- [ ] SQLite 數據存儲

### 🔄 Phase 2 - 功能擴展（規劃中）
- [ ] DEX 流動性監控
- [ ] 以太坊支援
- [ ] Web 儀表板
- [ ] 歷史數據分析

### 🔮 Phase 3 - 進階功能（未來）
- [ ] 機器學習異常檢測
- [ ] 多鏈監控
- [ ] 自動交易信號
- [ ] 容器化部署

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