# 遊戲資源目錄

本目錄包含敲磚塊遊戲的所有資源檔案，包括圖片、音效和字體。

## 📁 目錄結構

```
assets/
├── images/          # 圖片資源
├── sounds/          # 音效資源
├── fonts/           # 字體資源
└── README.md        # 本說明檔案
```

## 🖼️ 圖片資源 (images/)

### 預期的圖片檔案

| 檔案名稱             | 用途            | 建議尺寸 | 格式 |
| -------------------- | --------------- | -------- | ---- |
| `brick_normal.png`   | 普通磚塊        | 60x30    | PNG  |
| `brick_tnt.png`      | TNT 磚塊        | 60x30    | PNG  |
| `brick_blinking.png` | 閃爍磚塊        | 60x30    | PNG  |
| `ball.png`           | 球              | 20x20    | PNG  |
| `paddle.png`         | 底板            | 120x20   | PNG  |
| `explosion_01.png`   | 爆炸動畫第 1 幀 | 80x80    | PNG  |
| `explosion_02.png`   | 爆炸動畫第 2 幀 | 80x80    | PNG  |
| `explosion_03.png`   | 爆炸動畫第 3 幀 | 80x80    | PNG  |
| `particle.png`       | 粒子效果        | 4x4      | PNG  |
| `background.png`     | 背景圖片        | 800x600  | PNG  |
| `ui_game_over.png`   | 遊戲結束畫面    | 400x200  | PNG  |

### 設計規範

- **色彩風格**: 明亮、飽和的色調
- **像素風格**: 推薦使用像素藝術風格或清晰的向量圖形
- **透明度**: 使用 PNG 格式支援透明背景
- **一致性**: 保持所有圖片的藝術風格一致

## 🔊 音效資源 (sounds/)

### 預期的音效檔案

| 檔案名稱               | 用途         | 建議長度 | 格式 |
| ---------------------- | ------------ | -------- | ---- |
| `brick_hit.wav`        | 球撞擊磚塊   | 0.2 秒   | WAV  |
| `tnt_priming.wav`      | TNT 觸發音效 | 0.3 秒   | WAV  |
| `explosion.wav`        | TNT 爆炸音效 | 0.8 秒   | WAV  |
| `paddle_hit.wav`       | 球撞擊底板   | 0.2 秒   | WAV  |
| `wall_bounce.wav`      | 球撞擊牆壁   | 0.1 秒   | WAV  |
| `powerup_collect.wav`  | 收集道具     | 0.3 秒   | WAV  |
| `game_over.wav`        | 遊戲結束     | 1.0 秒   | WAV  |
| `background_music.ogg` | 背景音樂     | 循環     | OGG  |

### 音效規範

- **品質**: 16-bit, 44.1kHz 或更高
- **音量**: 統一音量級別，避免音效過響或過小
- **格式**: 短音效使用 WAV，長音樂使用 OGG
- **風格**: 8-bit 復古風格或現代電子音效

## 🔤 字體資源 (fonts/)

### 預期的字體檔案

| 檔案名稱         | 用途         | 風格     | 格式 |
| ---------------- | ------------ | -------- | ---- |
| `game_font.ttf`  | 主要遊戲文字 | 像素風格 | TTF  |
| `ui_font.ttf`    | 介面文字     | 清晰易讀 | TTF  |
| `score_font.ttf` | 得分顯示     | 粗體數字 | TTF  |

### 字體規範

- **可讀性**: 確保在小尺寸下仍然清晰
- **風格**: 與遊戲整體風格協調
- **授權**: 使用開源或已授權的字體

## 📝 使用方式

### 在程式中載入資源

```python
# 在 config.py 中定義資源路徑
import os

ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# 圖片路徑
IMAGE_PATHS = {
    "brick_normal": os.path.join(IMAGES_DIR, "brick_normal.png"),
    "brick_tnt": os.path.join(IMAGES_DIR, "brick_tnt.png"),
    "ball": os.path.join(IMAGES_DIR, "ball.png"),
    "paddle": os.path.join(IMAGES_DIR, "paddle.png"),
}

# 音效路徑
SOUND_PATHS = {
    "brick_hit": os.path.join(SOUNDS_DIR, "brick_hit.wav"),
    "explosion": os.path.join(SOUNDS_DIR, "explosion.wav"),
    "paddle_hit": os.path.join(SOUNDS_DIR, "paddle_hit.wav"),
}

# 字體路徑
FONT_PATHS = {
    "game_font": os.path.join(FONTS_DIR, "game_font.ttf"),
    "ui_font": os.path.join(FONTS_DIR, "ui_font.ttf"),
}
```

### 資源載入範例

```python
import pygame
import os
from config import IMAGE_PATHS, SOUND_PATHS

class ResourceManager:
    """資源管理器"""

    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.load_all_resources()

    def load_all_resources(self):
        """載入所有資源"""
        self.load_images()
        self.load_sounds()

    def load_images(self):
        """載入所有圖片"""
        for name, path in IMAGE_PATHS.items():
            if os.path.exists(path):
                try:
                    self.images[name] = pygame.image.load(path)
                    print(f"已載入圖片: {name}")
                except pygame.error as e:
                    print(f"無法載入圖片 {name}: {e}")
            else:
                print(f"圖片檔案不存在: {path}")

    def load_sounds(self):
        """載入所有音效"""
        for name, path in SOUND_PATHS.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"已載入音效: {name}")
                except pygame.error as e:
                    print(f"無法載入音效 {name}: {e}")
            else:
                print(f"音效檔案不存在: {path}")

    def get_image(self, name):
        """獲取圖片"""
        return self.images.get(name)

    def get_sound(self, name):
        """獲取音效"""
        return self.sounds.get(name)

    def play_sound(self, name, volume=1.0):
        """播放音效"""
        sound = self.get_sound(name)
        if sound:
            sound.set_volume(volume)
            sound.play()

# 全域資源管理器
resource_manager = ResourceManager()
```

## 🎨 資源創建指南

### 自製圖片資源

1. **使用免費工具**:

   - [GIMP](https://www.gimp.org/) - 免費圖片編輯軟體
   - [Aseprite](https://www.aseprite.org/) - 像素藝術專用（付費）
   - [Piskel](https://www.piskelapp.com/) - 線上像素藝術編輯器

2. **設計提示**:
   - 保持簡潔明亮的色彩
   - 使用明確的邊框和對比度
   - 考慮動畫需求（如爆炸效果）

### 自製音效資源

1. **使用免費工具**:

   - [Audacity](https://www.audacityteam.org/) - 免費音效編輯軟體
   - [sfxr](http://www.drpetter.se/project_sfxr.html) - 8-bit 音效生成器
   - [Freesound](https://freesound.org/) - 免費音效庫

2. **音效提示**:
   - 保持簡短有力
   - 避免版權問題
   - 測試在遊戲中的效果

## 📄 授權資訊

- 請確保所有使用的資源都有適當的授權
- 建議使用 Creative Commons 或其他開源授權的資源
- 記錄資源的來源和授權資訊

## 🔗 推薦資源網站

### 免費圖片資源

- [OpenGameArt](https://opengameart.org/)
- [itch.io](https://itch.io/game-assets)
- [Kenney](https://www.kenney.nl/assets)

### 免費音效資源

- [Freesound](https://freesound.org/)
- [Zapsplat](https://www.zapsplat.com/)
- [BBC Sound Effects](http://bbcsfx.acropolis.org.uk/)

### 免費字體資源

- [Google Fonts](https://fonts.google.com/)
- [Font Squirrel](https://www.fontsquirrel.com/)
- [DaFont](https://www.dafont.com/)
