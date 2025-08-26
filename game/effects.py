# -*- coding: utf-8 -*-
"""
遊戲特效系統模組

包含爆炸效果、磚塊碎片、彩蛋等視覺特效類別。
"""

######################載入套件######################
import pygame
import math
import random

######################導入設定######################
from config import EFFECTS_CONFIG, COLORS

######################音效載入######################
# 嘗試載入爆炸音效（若不存在則忽略）
EXPLOSION_SOUND = None
try:
    # 檢查 mixer 是否已初始化
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception:
            pass
    sound_path = "assets/sounds/explosion.wav"
    EXPLOSION_SOUND = pygame.mixer.Sound(sound_path)
except Exception:
    # 如果載入失敗就不播放音效，遊戲仍然可以正常運行
    EXPLOSION_SOUND = None


######################物件類別######################


class Explosion:
    """
    爆炸效果類別\n
    \n
    產生擴散式的圓圈爆炸動畫，用於 TNT 爆炸時的視覺效果。\n
    爆炸會從小圓圈逐漸擴大，顏色從亮橙色漸變到透明。\n
    \n
    特性:\n
    1. 多層圓圈效果，創造深度感\n
    2. 漸變透明度，模擬爆炸消散\n
    3. 自動播放音效（如果有載入）\n
    \n
    屬性:\n
    x, y (float): 爆炸中心座標\n
    radius (float): 當前爆炸半徑\n
    max_radius (int): 最大爆炸半徑\n
    duration (int): 爆炸持續的幀數\n
    timer (int): 當前經過的幀數\n
    \n
    使用範例:\n
    explosion = Explosion(100, 200)  # 在指定位置創建爆炸\n
    while explosion.update():  # 每幀更新\n
        explosion.draw(screen)  # 繪製爆炸效果\n
    """

    def __init__(self, x, y):
        """
        初始化爆炸效果\n
        \n
        參數:\n
        x (float): 爆炸中心 X 座標\n
        y (float): 爆炸中心 Y 座標\n
        """
        self.x = x
        self.y = y
        self.radius = 0  # 從 0 開始擴散
        self.max_radius = EFFECTS_CONFIG["EXPLOSION_MAX_RADIUS"]
        self.duration = EFFECTS_CONFIG["EXPLOSION_DURATION"]
        self.timer = 0

        # 嘗試播放爆炸音效（如果有載入的話）
        try:
            if EXPLOSION_SOUND:
                EXPLOSION_SOUND.play()
        except Exception:
            # 音效播放失敗也不影響遊戲運行
            pass

    def update(self):
        """更新爆炸效果"""
        self.timer += 1
        self.radius = (self.timer / self.duration) * self.max_radius
        return self.timer < self.duration

    def draw(self, surface):
        """繪製爆炸效果"""
        if self.timer < self.duration:
            # 創建多層圓圈效果
            alpha = 255 - int((self.timer / self.duration) * 255)
            for i in range(3):
                radius = self.radius - i * 15
                if radius > 0:
                    color_intensity = max(0, alpha - i * 50)
                    color = (255, min(255, color_intensity + 100), 0)  # 橙紅色
                    pygame.draw.circle(
                        surface, color, (int(self.x), int(self.y)), int(radius), 3
                    )


class Shard:
    """磚塊碎片小方塊，簡單的物理與生命週期"""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        # 初始速度帶有隨機性
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-7.0, -2.0)
        self.size = random.randint(
            EFFECTS_CONFIG["SHARD_SIZE_MIN"], EFFECTS_CONFIG["SHARD_SIZE_MAX"]
        )
        self.color = color
        self.life = random.randint(
            EFFECTS_CONFIG["SHARD_LIFE_MIN"], EFFECTS_CONFIG["SHARD_LIFE_MAX"]
        )
        self.timer = 0

    def update(self, screen_height=600):
        """更新碎片位置和狀態"""
        # 重力
        self.vy += EFFECTS_CONFIG["GRAVITY"]
        # 空氣阻力
        self.vx *= EFFECTS_CONFIG["AIR_RESISTANCE"]
        self.vy *= 0.999
        self.x += self.vx
        self.y += self.vy
        self.timer += 1

        # 邊界外或生命結束就移除
        if self.timer >= self.life or self.y > screen_height + 200:
            return False
        return True

    def draw(self, surface):
        """繪製碎片"""
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(int(self.x), int(self.y), self.size, self.size),
        )


class Egg:
    """簡單的彩蛋物件，會緩慢下落，碰到板子則觸發撿取效果"""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vy = random.uniform(1.0, 3.0)
        self.radius = 8
        self.collected = False
        # 顏色與裝飾
        self.color = COLORS["PINK"]

    def update(self, screen_height=600):
        """更新彩蛋位置"""
        self.y += self.vy
        # 若落出畫面則刪除
        return not self.collected and self.y < screen_height + 100

    def draw(self, surface):
        """繪製彩蛋"""
        rect = pygame.Rect(
            int(self.x) - self.radius,
            int(self.y) - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        pygame.draw.ellipse(surface, self.color, rect)
        # 白色高光
        pygame.draw.ellipse(
            surface,
            COLORS["WHITE"],
            (int(self.x) - 3, int(self.y) - self.radius + 2, 6, 4),
        )

    def check_paddle_collision(self, paddle):
        """檢查是否與底板碰撞"""
        if (
            self.y + self.radius >= paddle.y
            and self.x >= paddle.x
            and self.x <= paddle.x + paddle.width
        ):
            self.collected = True
            return True
        return False
