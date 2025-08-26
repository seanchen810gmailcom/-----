# -*- coding: utf-8 -*-
"""
敲磚塊遊戲設定檔

包含所有遊戲常數和設定參數，方便調整遊戲體驗。
"""

# 視窗設定
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "敲磚塊遊戲"
FPS = 60

# 顏色設定 (R, G, B)
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "ORANGE": (255, 165, 0),
    "PURPLE": (128, 0, 128),
    "PINK": (255, 192, 203),
    # 磚塊顏色
    "BRICK_TOMATO": (255, 99, 71),
    "BRICK_ORANGE": (255, 165, 0),
    "BRICK_GOLD": (255, 215, 0),
    "BRICK_SEA_GREEN": (60, 179, 113),
    "BRICK_ROYAL_BLUE": (65, 105, 225),
    "BRICK_TNT": (139, 69, 19),  # 棕色
    # 特殊效果顏色
    "EXPLOSION_ORANGE": (255, 165, 0),
    "SHARD_COLORS": [(255, 99, 71), (255, 165, 0), (255, 215, 0)],
    # 閃爍磚塊調色盤
    "BLINK_PALETTE": [
        (173, 216, 230),  # lightblue
        (135, 206, 250),  # skyblue
        (65, 105, 225),  # royal blue
        (0, 0, 139),  # dark blue
    ],
}

# 磚塊設定
BRICK_CONFIG = {
    "COLS": 10,
    "ROWS": 5,
    "WIDTH": None,  # 動態計算
    "HEIGHT": 30,
    "MARGIN_LEFT": 40,
    "MARGIN_TOP": 60,
    "SPACING_X": 10,
    "SPACING_Y": 10,
    "TNT_COUNT": 5,  # TNT 磚塊數量
    "BLINKING_COUNT": 6,  # 閃爍磚塊數量
}

# 底板設定
PADDLE_CONFIG = {
    "WIDTH": 120,
    "HEIGHT": 20,
    "COLOR": COLORS["WHITE"],
    "SPEED": 10,
    "MARGIN_BOTTOM": 50,  # 距離底部的距離
}

# 球設定
BALL_CONFIG = {
    "RADIUS": 10,
    "COLOR": COLORS["YELLOW"],
    "SPEED": 7,
    "MAX_SPEED": 9,
}

# TNT 設定
TNT_CONFIG = {
    "EXPLOSION_RADIUS": 100,  # 爆炸半徑（像素）
    "BLINK_DURATION": 500,  # 閃爍持續時間（毫秒）
    "BLINK_REPEATS": 3,  # 閃爍重複次數
    "SCORE_PER_EXPLOSION": 100,  # TNT 爆炸得分
}

# 特效設定
EFFECTS_CONFIG = {
    "EXPLOSION_MAX_RADIUS": 80,
    "EXPLOSION_DURATION": 30,  # 爆炸持續幀數
    "SHARD_COUNT": 10,  # 每個磚塊產生的碎片數量
    "SHARD_LIFE_MIN": 40,  # 碎片最小生命週期（幀）
    "SHARD_LIFE_MAX": 80,  # 碎片最大生命週期（幀）
    "SHARD_SIZE_MIN": 2,  # 碎片最小尺寸
    "SHARD_SIZE_MAX": 6,  # 碎片最大尺寸
    "GRAVITY": 0.35,  # 重力加速度
    "AIR_RESISTANCE": 0.995,  # 空氣阻力係數
}

# 閃爍磚塊設定
BLINKING_CONFIG = {
    "PERIOD": 1200,  # 閃爍週期（毫秒）
    "EXTRA_BALLS": 2,  # 撞擊時產生的額外球數
}

# 得分設定
SCORE_CONFIG = {
    "BRICK_HIT": 100,  # 擊中普通磚塊得分
    "TNT_EXPLOSION": 100,  # TNT 爆炸得分
    "TNT_DESTROYED": 100,  # 被 TNT 炸掉的磚塊得分
    "EGG_COLLECTED": 250,  # 撿取彩蛋得分
}

# 字體設定
FONT_CONFIG = {
    "DEFAULT_SIZE": 36,
    "LARGE_SIZE": 74,
    "TNT_TEXT_SIZE": 24,
}

# 物理設定
PHYSICS_CONFIG = {
    "BOUNCE_ANGLE_MAX": 60,  # 最大反彈角度（度）
    "FALL_SPEED": 2,  # 磚塊下落速度
}

# 遊戲規則設定
GAME_CONFIG = {
    "TOTAL_BRICKS": BRICK_CONFIG["COLS"] * BRICK_CONFIG["ROWS"],
    "AUTO_RESTART": False,  # 是否自動重新開始
    "SHOW_DEBUG_INFO": False,  # 是否顯示除錯資訊
}


# 計算動態設定值
def calculate_brick_width():
    """計算磚塊寬度以填滿可用空間"""
    available_width = (
        WINDOW_WIDTH
        - 2 * BRICK_CONFIG["MARGIN_LEFT"]
        - (BRICK_CONFIG["COLS"] - 1) * BRICK_CONFIG["SPACING_X"]
    )
    return available_width // BRICK_CONFIG["COLS"]


# 設定動態計算的值
BRICK_CONFIG["WIDTH"] = calculate_brick_width()

# 磚塊行顏色配置
ROW_COLORS = [
    COLORS["BRICK_TOMATO"],
    COLORS["BRICK_ORANGE"],
    COLORS["BRICK_GOLD"],
    COLORS["BRICK_SEA_GREEN"],
    COLORS["BRICK_ROYAL_BLUE"],
]
