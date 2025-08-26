# 敲磚塊遊戲（Breakout Game）v2.0

一個使用 Python 和 Pygame 開發的模組化敲磚塊遊戲，具有 TNT 特殊磚塊功能和完整的測試覆蓋。

## 🎮 遊戲特色

- **經典敲磚塊玩法**：使用底板反彈球來擊破磚塊
- **TNT 特殊磚塊**：隨機生成的 TNT 磚塊可產生爆炸效果和連鎖反應
- **閃爍特殊磚塊**：撞擊後會產生額外球體，增加遊戲樂趣
- **模組化架構**：清晰的程式結構，易於維護和擴展
- **完整測試覆蓋**：包含單元測試、整合測試和效能測試
- **多彩視覺效果**：爆炸動畫、碎片效果和流暢的遊戲體驗

## 🚀 快速開始

### 系統需求

- Python 3.7 或更高版本
- Pygame 2.1.0 或更高版本

### 安裝與執行

1. **克隆專案**

   ```bash
   git clone <repository-url>
   cd 敲磚塊遊戲
   ```

2. **建立虛擬環境（推薦）**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # 或
   .venv\Scripts\activate     # Windows
   ```

3. **安裝相依套件**

   ```bash
   make install
   # 或
   pip install -r requirements.txt
   ```

4. **執行遊戲**
   ```bash
   make run
   # 或
   python main_new.py
   ```

## 🛠️ 開發工具

本專案包含完整的開發工具鏈，使用 `make` 命令快速執行常見任務：

```bash
make help           # 顯示所有可用命令
make install        # 安裝依賴套件
make test           # 執行所有測試
make test-quick     # 執行快速測試
make coverage       # 測試覆蓋率分析
make lint           # 程式碼品質檢查
make format         # 自動格式化程式碼
make clean          # 清理暫存檔案
make package        # 打包應用程式
```

## 🎯 遊戲操作

| 按鍵/操作      | 功能                   |
| -------------- | ---------------------- |
| **← → 或 A D** | 移動底板               |
| **SPACE**      | 暫停/繼續遊戲          |
| **R**          | 重新開始遊戲           |
| **ESC**        | 退出遊戲               |
| **滑鼠左鍵**   | 放置 TNT（如果有的話） |

## 📁 專案結構

```
敲磚塊遊戲/
├── main_new.py             # 重構後的遊戲主程式
├── main.py                 # 原始主程式（保留參考）
├── config.py               # 遊戲設定和常數
├── requirements.txt        # Python 相依套件清單
├── setup.py                # 套件安裝設定
├── Makefile                # 開發工具命令
├── game/                   # 遊戲核心模組
│   ├── __init__.py
│   ├── objects.py          # 遊戲物件 (Brick, Ball, Paddle)
│   ├── effects.py          # 特效系統 (Explosion, Shard, Egg)
│   ├── utils.py            # 工具函數 (TNT爆炸, 碎片生成)
│   └── game_logic.py       # 遊戲邏輯和狀態管理
├── tests/                  # 完整測試套件
│   ├── __init__.py
│   ├── run_tests.py        # 測試執行器
│   ├── test_objects.py     # 物件類別測試
│   ├── test_effects.py     # 特效系統測試
│   ├── test_utils.py       # 工具函數測試
│   ├── test_game_logic.py  # 遊戲邏輯測試
│   ├── test_tnt.py         # TNT 功能測試
│   └── test_integration.py # 整合測試
├── assets/                 # 遊戲資源
│   ├── images/             # 圖片資源
│   ├── sounds/             # 音效資源
│   └── fonts/              # 字體資源
├── docs/                   # 專案文件
│   ├── README.md           # 詳細說明文件
│   ├── TNT_功能說明.md     # TNT 功能說明
│   ├── API.md              # API 文件
│   └── 開發指南.md         # 開發指南
└── __pycache__/            # Python 快取檔案
```

## 🧪 測試

### 執行測試

```bash
# 使用測試執行器（推薦）
python tests/run_tests.py all          # 所有測試
python tests/run_tests.py quick        # 快速測試
python tests/run_tests.py coverage     # 覆蓋率分析

# 使用 make 命令
make test           # 所有測試
make test-quick     # 快速測試
make coverage       # 覆蓋率分析

# 執行特定測試
python tests/run_tests.py tests.test_objects
python tests/run_tests.py tests.test_tnt.test_tnt_explosion
```

### 測試涵蓋範圍

- **單元測試**：每個類別和函數的獨立測試
- **整合測試**：模組間的互動測試
- **效能測試**：遊戲效能和記憶體使用測試
- **TNT 系統測試**：完整的爆炸機制測試

## 📚 文件

- [詳細說明文件](docs/README.md) - 完整的遊戲說明和使用手冊
- [TNT 功能說明](docs/TNT_功能說明.md) - TNT 磚塊系統的詳細介紹
- [API 文件](docs/API.md) - 程式介面說明
- [開發指南](docs/開發指南.md) - 開發者參考資料

## 🎲 遊戲機制

### TNT 磚塊系統

- 每局隨機生成可配置數量的 TNT 磚塊
- 撞擊後進入紅白閃爍倒數（可配置時間）
- 爆炸範圍可調整，支援連鎖反應
- 廣度優先搜尋演算法確保連鎖爆炸的正確性

### 閃爍磚塊系統

- 隨機生成特殊磚塊
- 撞擊後產生額外球體
- 增加遊戲的策略性和樂趣

### 得分系統

- 普通磚塊：可配置分數
- TNT 爆炸：獎勵分數
- 被 TNT 炸掉的磚塊：連鎖獎勵
- 撿取彩蛋：特殊獎勵

## 🛠️ 開發

### 模組架構

- **`config.py`**: 集中式配置管理，所有參數可調整
- **`game/objects.py`**: 核心遊戲物件，遵循面向物件設計
- **`game/effects.py`**: 獨立的視覺特效系統
- **`game/utils.py`**: 純函數工具，易於測試
- **`game/game_logic.py`**: 狀態管理，單一責任原則

### 設定自訂

編輯 `config.py` 檔案來調整遊戲參數：

```python
# 修改遊戲視窗大小
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# 調整 TNT 爆炸範圍
TNT_CONFIG = {
    "EXPLOSION_RADIUS": 150,
    "COUNTDOWN_DURATION": 2000,  # 毫秒
    "CHAIN_REACTION": True
}

# 修改磚塊配置
BRICK_CONFIG = {
    "TNT_COUNT": 8,
    "BLINKING_COUNT": 6,
    "SCORE_VALUE": 100
}
```

### 程式碼品質

```bash
make lint           # 執行 flake8 和 isort 檢查
make format         # 使用 black 和 isort 格式化
make clean          # 清理暫存檔案
```

## 🔄 遷移指南

### 從舊版本升級

如果你有舊版本的遊戲：

1. **備份原始檔案**

   ```bash
   cp main.py main_old.py
   ```

2. **使用新架構**

   ```bash
   python main_new.py
   ```

3. **遷移自訂設定**
   - 將舊的硬編碼參數移到 `config.py`
   - 更新任何自訂功能以使用新的模組結構

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 專案
2. 創建功能分支：`git checkout -b feature/新功能`
3. 執行測試：`make test`
4. 提交變更：`git commit -am '新增某功能'`
5. 推送分支：`git push origin feature/新功能`
6. 建立 Pull Request

## 📄 授權

本專案採用 MIT 授權條款。

## 🔮 未來計劃

### v2.1 計劃

- [ ] 音效系統整合
- [ ] 存檔/讀檔功能
- [ ] 更多特殊磚塊類型

### v3.0 願景

- [ ] 多關卡系統
- [ ] 道具系統
- [ ] 線上排行榜
- [ ] 手機觸控支援

## 📊 效能指標

- **啟動時間**: < 2 秒
- **記憶體使用**: < 50MB
- **幀率**: 穩定 60 FPS
- **測試覆蓋率**: > 90%

---

享受遊戲吧！ 🎮✨

_v2.0 - 模組化重構版本，更穩定、更易維護、更易測試_
