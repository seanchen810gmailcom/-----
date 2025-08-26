# -*- coding: utf-8 -*-
"""
簡單的敲磚塊遊戲範例（single-file demo），已加入中文註解以便學習。

說明：
- 目前程式只會在視窗中畫出兩個磚塊
- 範例保留了最小可執行架構：初始化、物件類別、主迴圈、繪製
- 你可以在註解中找到要擴充（例如球與底板）的建議位置
"""

import pygame
import sys
import math
import random
from collections import deque


###################### 物件類別：磚塊 ######################
class Brick:
    """代表一個磚塊的簡單類別。

    建構子參數：x, y, width, height, color, is_tnt
    屬性：
      - hit: 是否已被擊中（被擊中後可設為 True 以避免繪製）
      - is_tnt: 是否為TNT磚塊
    """

    def __init__(self, x, y, width, height, color, is_tnt=False):
        # 磚塊左上角座標
        self.x = x
        self.y = y
        # 磚塊大小
        self.width = width
        self.height = height
        # 顏色為 (R, G, B)
        self.color = color
        # 保存原始顏色（用於重置）
        self.base_color = color
        # 被擊中狀態
        self.hit = False
        # 是否為TNT磚塊
        self.is_tnt = is_tnt
        # TNT 觸發（priming）相關狀態
        # 被球擊中時不立即爆炸，而是進入閃爍倒數狀態
        self.tnt_primed = False
        # 以 pygame.time.get_ticks() 為基準的起始時間（毫秒）
        self.tnt_primed_start = 0
        # 已完成的紅白週期數（每個週期為紅0.5s + 白0.5s）
        self.tnt_primed_cycles = 0
        # 單一紅或白的持續時間（毫秒）
        self.tnt_blink_duration = 500
        # 要重複的紅白週期數，達到後爆炸
        self.tnt_blink_repeats = 3
        # 是否為會閃爍（特殊）磚塊
        self.is_blinking = False
        # 閃爍參數（毫秒為單位）
        self.blink_period = 1200
        # 隨機位移讓多顆磚的閃爍不同步
        self.blink_offset = random.randint(0, 1000)
        # 下落相關屬性
        self.falling = False
        self.target_y = y
        self.fall_speed = 2

    def draw(self, surface):
        """在傳入的 surface 上繪製磚塊（若尚未被擊中）。"""
        if not self.hit:
            draw_color = self.color
            # 如果是會閃爍的磚塊，計算漸變色（淡藍色的亮/微暗變化）
            if self.is_blinking:
                # 使用多段藍色調來擴大閃爍的色階幅度：
                # 淺藍 -> 天空藍 -> 皇家藍 -> 深藍
                palette = [
                    (173, 216, 230),  # lightblue
                    (135, 206, 250),  # skyblue
                    (65, 105, 225),  # royal blue
                    (0, 0, 139),  # dark blue
                ]
                # 計算 0..1 的週期值，使用正弦讓變化平滑
                t = (pygame.time.get_ticks() + self.blink_offset) % self.blink_period
                factor = (math.sin(2 * math.pi * (t / self.blink_period)) * 0.5) + 0.5

                # 將 factor 映射到 palette 的多段區間並做線性內插
                segs = len(palette) - 1
                scaled = factor * segs
                idx = int(scaled)
                frac = scaled - idx
                # 保險處理邊界
                idx = max(0, min(idx, segs - 1))
                c1 = palette[idx]
                c2 = palette[min(idx + 1, segs)]
                draw_color = (
                    int(c1[0] * (1 - frac) + c2[0] * frac),
                    int(c1[1] * (1 - frac) + c2[1] * frac),
                    int(c1[2] * (1 - frac) + c2[2] * frac),
                )

            # 如果是被觸發的 TNT，優先以紅/白閃爍顏色顯示
            if self.is_tnt and self.tnt_primed and not self.hit:
                # 計算目前階段（紅或白）
                t = pygame.time.get_ticks() - self.tnt_primed_start
                period = self.tnt_blink_duration * 2
                phase = (t % period) < self.tnt_blink_duration
                # phase True 表示紅色階段，False 表示白色
                draw_color = (255, 0, 0) if phase else (255, 255, 255)

            pygame.draw.rect(
                surface,
                draw_color,
                pygame.Rect(self.x, self.y, self.width, self.height),
            )

            # 如果是TNT磚塊，在上面繪製 "TNT" 文字
            if self.is_tnt:
                font = pygame.font.Font(None, 24)
                text = font.render("TNT", True, (255, 255, 255))  # 白色文字
                text_rect = text.get_rect(
                    center=(self.x + self.width // 2, self.y + self.height // 2)
                )
                surface.blit(text, text_rect)

    def start_priming(self):
        """當球打到 TNT 時呼叫，開始紅白閃爍倒數。

        若已在倒數中則不重複啟動。
        """
        if not self.is_tnt:
            return
        if self.tnt_primed or self.hit:
            return
        self.tnt_primed = True
        self.tnt_primed_start = pygame.time.get_ticks()
        self.tnt_primed_cycles = 0

    def update(self, now, all_bricks):
        """每幀更新磚塊的狀態：用於處理 TNT 的閃爍與爆炸觸發，以及下落動畫。

        - now: pygame.time.get_ticks()
        - all_bricks: 傳入整個磚塊列表以便爆炸時傳遞
        """
        # 處理下落動畫
        if self.falling:
            if self.y < self.target_y:
                self.y += self.fall_speed
                if self.y >= self.target_y:
                    self.y = self.target_y
                    self.falling = False

        # 只處理未被摧毀且已經進入 priming 的 TNT
        if self.is_tnt and self.tnt_primed and not self.hit:
            elapsed = now - self.tnt_primed_start
            one_cycle = self.tnt_blink_duration * 2
            cycles_completed = elapsed // one_cycle
            # 當達到設定的 cycle 次數後觸發爆炸
            if cycles_completed >= self.tnt_blink_repeats:
                # 呼叫爆炸處理（explode_tnt 會標記 self.hit 等）
                explode_tnt(self, all_bricks)
                # 關閉 priming（explode_tnt 會標記 hit）
                self.tnt_primed = False
            else:
                # 否則僅更新 cycle 計數（視覺由 draw 計算）
                self.tnt_primed_cycles = cycles_completed


###################### TNT爆炸函數 ######################
def explode_tnt(tnt_brick, all_bricks):
    """處理TNT磚塊爆炸，炸掉周圍的磚塊。

    參數：
    - tnt_brick: 被擊中的TNT磚塊
    - all_bricks: 所有磚塊的列表

    返回：
    - 被炸掉的磚塊數量
    """
    global score, explosions

    # 使用佇列處理連鎖爆炸（BFS）
    exploded_count = 0
    explosion_radius = 100  # 爆炸半徑（像素）

    queue = deque()

    # 添加爆炸效果
    explosion_x = tnt_brick.x + tnt_brick.width // 2
    explosion_y = tnt_brick.y + tnt_brick.height // 2
    explosions.append(Explosion(explosion_x, explosion_y))

    # 若傳入的 tnt_brick 尚未被標記為 hit（例如在測試中），則先標記並計數
    if not tnt_brick.hit:
        tnt_brick.hit = True
        exploded_count += 1
        score += 100  # TNT 爆炸也得分

    # 無論如何，將這顆 TNT 加入處理佇列以檢查其範圍內的磚塊
    queue.append(tnt_brick)

    while queue:
        current = queue.popleft()
        cur_center_x = current.x + current.width // 2
        cur_center_y = current.y + current.height // 2

        # 檢查所有尚未被摧毀的磚塊
        for brick in all_bricks:
            if brick.hit:
                continue

            brick_center_x = brick.x + brick.width // 2
            brick_center_y = brick.y + brick.height // 2
            distance = math.hypot(
                cur_center_x - brick_center_x, cur_center_y - brick_center_y
            )

            if distance <= explosion_radius:
                # 這個磚塊會被炸掉
                brick.hit = True
                # 產生碎片
                try:
                    spawn_shards(brick, count=10)
                except Exception:
                    pass
                exploded_count += 1
                score += 100  # 每個被炸掉的磚塊得100分

                # 如果被炸到的也是TNT，加入佇列以觸發連鎖，並添加爆炸效果
                if brick.is_tnt:
                    queue.append(brick)
                    explosion_x = brick.x + brick.width // 2
                    explosion_y = brick.y + brick.height // 2
                    explosions.append(Explosion(explosion_x, explosion_y))

    return exploded_count


###################### 物件類別：玩家底板 ######################
class Paddle:
    """代表玩家控制的底板。

    建構子參數：x, y, width, height, color, speed
    屬性：
      - speed: 移動速度（像素/幀）
    """

    def __init__(self, x, y, width, height, color, speed):
        # 底板左上角座標
        self.x = x
        self.y = y
        # 底板大小
        self.width = width
        self.height = height
        # 顏色為 (R, G, B)
        self.color = color
        # 移動速度
        self.speed = speed

    def move_left(self, screen_width):
        """向左移動，但不能超出螢幕左邊界。"""
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self, screen_width):
        """向右移動，但不能超出螢幕右邊界。"""
        self.x += self.speed
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width

    def draw(self, surface):
        """在傳入的 surface 上繪製底板。"""
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(self.x, self.y, self.width, self.height),
        )


###################### 物件類別：球 ######################
class Ball:
    """代表遊戲中的球。

    建構子參數：x, y, radius, color, speed
    屬性：
      - speed: 球的移動速度
      - vx, vy: x和y方向的速度分量
      - stuck: 是否黏在底板上
    """

    def __init__(self, x, y, radius, color, speed):
        # 球的中心座標
        self.x = x
        self.y = y
        # 球的半徑
        self.radius = radius
        # 顏色為 (R, G, B)
        self.color = color
        # 移動速度
        self.speed = speed
        # 速度分量（開始時為0，因為球黏在底板上）
        self.vx = 0
        self.vy = 0
        # 是否黏在底板上
        self.stuck = True
        # 勝利繞圈的參數（初始化於此）
        self.spinning = False
        self.spin_center_x = 0
        self.spin_center_y = 0
        self.spin_radius = 0
        self.spin_angle = 0.0
        self.spin_angular_speed = 0.15  # 弧度/幀

    def update(self, paddle, bricks, screen_width, screen_height, balls_list=None):
        """更新球的位置並處理碰撞。"""
        # 球速在本需求中固定為常數（BALL_SPEED），不會在遊戲過程中改變

        if self.stuck:
            # 球黏在底板上，跟隨底板移動
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - self.radius
            return True  # 遊戲繼續

        # 更新球的位置
        self.x += self.vx
        self.y += self.vy

        # 檢查與邊界的碰撞（左右邊界）
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            self.vx = -self.vx
            # 確保球不會卡在邊界外
            if self.x - self.radius <= 0:
                self.x = self.radius
            else:
                self.x = screen_width - self.radius
            # 保持速度大小為設定的 speed
            self.normalize_velocity()

        # 檢查與上邊界的碰撞
        if self.y - self.radius <= 0:
            self.vy = -self.vy
            self.y = self.radius
            # 保持速度大小為設定的 speed
            self.normalize_velocity()

        # 檢查與下邊界的碰撞（遊戲結束）
        if self.y + self.radius >= screen_height:
            return False  # 遊戲結束

        # 檢查與底板的碰撞
        if (
            self.y + self.radius >= paddle.y
            and self.y - self.radius <= paddle.y + paddle.height
            and self.x >= paddle.x
            and self.x <= paddle.x + paddle.width
        ):

            # 計算球撞到底板的相對位置（0到1之間）
            hit_pos = (self.x - paddle.x) / paddle.width

            # 根據撞擊位置調整反彈角度（-60度到+60度）
            max_angle = math.radians(60)
            angle = (hit_pos - 0.5) * 2 * max_angle  # -max_angle..+max_angle

            # 以 angle 計算新的速度分量（向上為負的 vy），速度大小固定為 self.speed
            self.vx = self.speed * math.sin(angle)
            self.vy = -self.speed * math.cos(angle)

            # 確保球不會卡在底板裡
            self.y = paddle.y - self.radius

        # 檢查與磚塊的碰撞
        for brick in bricks:
            if not brick.hit and self.check_brick_collision(brick):
                # 若是 TNT，啟動 priming（閃爍倒數）而不是立即爆炸
                if brick.is_tnt:
                    brick.start_priming()
                else:
                    # 非 TNT 磚塊直接標記為被擊中
                    brick.hit = True
                    # 產生碎片效果
                    try:
                        spawn_shards(brick, count=8)
                    except Exception:
                        pass
                    # 增加得分（全域變數）
                    global score
                    score += 100

                # 如果撞到的是會閃爍的特殊磚塊，額外生成兩顆球（若有提供 balls_list）
                if brick.is_blinking and balls_list is not None:
                    # 產生兩顆新球，位置為撞擊位置附近，速度為隨機方向
                    for _ in range(2):
                        nb = Ball(self.x, self.y, self.radius, self.color, self.speed)
                        nb.stuck = False
                        # 以稍微不同的隨機角度發射
                        angle = random.uniform(-math.pi, math.pi)
                        nb.vx = math.cos(angle) * nb.speed
                        nb.vy = math.sin(angle) * nb.speed
                        balls_list.append(nb)

                # 簡單的反彈邏輯
                if self.x < brick.x or self.x > brick.x + brick.width:
                    self.vx = -self.vx
                if self.y < brick.y or self.y > brick.y + brick.height:
                    self.vy = -self.vy

                # 撞到磚塊時反彈，並確保速度大小為 self.speed（不改變 speed）
                angle = math.atan2(self.vy, self.vx)
                self.vx = math.cos(angle) * self.speed
                self.vy = math.sin(angle) * self.speed

                break

        return True  # 遊戲繼續

    def check_brick_collision(self, brick):
        """檢查球是否與磚塊碰撞。"""
        # 找到最接近球心的磚塊上的點
        closest_x = max(brick.x, min(self.x, brick.x + brick.width))
        closest_y = max(brick.y, min(self.y, brick.y + brick.height))

        # 計算距離
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y

        return distance_squared < (self.radius * self.radius)

    def launch(self):
        """發射球（當按下上鍵時）。"""
        if self.stuck:
            self.stuck = False
            self.vx = 0
            self.vy = -self.speed

    def start_spin(self, center_x, center_y, radius=80):
        """開始繞著 (center_x, center_y) 繞圈，radius 為半徑。"""
        self.spinning = True
        self.spin_center_x = center_x
        self.spin_center_y = center_y
        self.spin_radius = radius
        # 從目前位置計算起始角度
        self.spin_angle = math.atan2(self.y - center_y, self.x - center_x)
        # 不改變球速；使用固定角速度繞圈
        self.spin_angular_speed = 0.12

        # 在繞圈時仍保持速度分量大小（但繞圈位置由角度計算決定）

    def update_spin(self):
        """每幀更新繞圈位置（在勝利時呼叫）。"""
        if not self.spinning:
            return
        # 更新角度
        self.spin_angle += self.spin_angular_speed
        # 計算新位置
        self.x = self.spin_center_x + math.cos(self.spin_angle) * self.spin_radius
        self.y = self.spin_center_y + math.sin(self.spin_angle) * self.spin_radius

    def draw(self, surface):
        """在傳入的 surface 上繪製球。"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def normalize_velocity(self):
        """將當前速度分量重新正規化，使速度大小等於 self.speed。

        如果當前速度為 0，則設定為向上移動（vy = -speed）。
        """
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            # 若沒有方向，預設向上
            self.vx = 0
            self.vy = -self.speed
            return
        self.vx = (self.vx / mag) * self.speed
        self.vy = (self.vy / mag) * self.speed


###################### 初始化 ######################
pygame.init()  # 啟動 Pygame

# 視窗大小設定（可自行調整）
WIDTH = 800
HEIGHT = 600

# 建立主視窗
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("敲磚塊遊戲")

# 控制畫面更新速率的時鐘物件
clock = pygame.time.Clock()


###################### 建立範例磚塊（改為 10 x 5 陣列） ######################
# 產生一個 10 列 x 5 行 的磚塊陣列（總共 50 顆），寬度會依視窗大小與左右邊距自動計算
BRICK_COLS = 10
BRICK_ROWS = 5
BRICK_MARGIN_LEFT = 40
BRICK_MARGIN_TOP = 60
BRICK_SPACING_X = 10
BRICK_SPACING_Y = 10
# 計算磚塊寬度以填滿可用空間（整數除法），高度固定
BRICK_WIDTH = (
    WIDTH - 2 * BRICK_MARGIN_LEFT - (BRICK_COLS - 1) * BRICK_SPACING_X
) // BRICK_COLS
BRICK_HEIGHT = 30


def create_new_bricks():
    """創建新的磚塊陣列，從視窗上方開始滑下"""
    new_bricks = []
    row_colors = [
        (255, 99, 71),  # tomato
        (255, 165, 0),  # orange
        (255, 215, 0),  # gold
        (60, 179, 113),  # medium sea green
        (65, 105, 225),  # royal blue
    ]

    # 首先創建所有磚塊（從視窗上方開始，y座標為負數讓它們滑下來）
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_MARGIN_LEFT + col * (BRICK_WIDTH + BRICK_SPACING_X)
            y = -BRICK_HEIGHT * (BRICK_ROWS - row) + row * (
                BRICK_HEIGHT + BRICK_SPACING_Y
            )  # 從上方開始
            color = row_colors[row % len(row_colors)]
            brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color)
            brick.target_y = BRICK_MARGIN_TOP + row * (
                BRICK_HEIGHT + BRICK_SPACING_Y
            )  # 目標位置
            brick.falling = True  # 標記為下落狀態
            new_bricks.append(brick)

    # 隨機選擇5個磚塊設為TNT磚塊
    tnt_indices = random.sample(range(len(new_bricks)), 5)
    for i in tnt_indices:
        new_bricks[i].is_tnt = True
        # TNT磚塊使用較暗的顏色以便區分
        new_bricks[i].color = (139, 69, 19)  # 棕色

    # 選擇 6 個非TNT 的磚塊設為會閃爍的特殊磚塊
    non_tnt_indices = [i for i in range(len(new_bricks)) if not new_bricks[i].is_tnt]
    if len(non_tnt_indices) >= 6:
        blinking_indices = random.sample(non_tnt_indices, 6)
    else:
        blinking_indices = non_tnt_indices
    for i in blinking_indices:
        new_bricks[i].is_blinking = True
        # 將基色改為較接近淡藍色，實際顏色由 draw 時 override
        new_bricks[i].color = new_bricks[i].base_color

    return new_bricks


bricks = []
row_colors = [
    (255, 99, 71),  # tomato
    (255, 165, 0),  # orange
    (255, 215, 0),  # gold
    (60, 179, 113),  # medium sea green
    (65, 105, 225),  # royal blue
]

# 首先創建所有磚塊（不設為TNT）
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        x = BRICK_MARGIN_LEFT + col * (BRICK_WIDTH + BRICK_SPACING_X)
        y = BRICK_MARGIN_TOP + row * (BRICK_HEIGHT + BRICK_SPACING_Y)
        color = row_colors[row % len(row_colors)]
        brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color)
        brick.target_y = y  # 初始磚塊已在目標位置
        brick.falling = False  # 不下落
        bricks.append(brick)

# 隨機選擇5個磚塊設為TNT磚塊
tnt_indices = random.sample(range(len(bricks)), 5)
for i in tnt_indices:
    bricks[i].is_tnt = True
    # TNT磚塊使用較暗的顏色以便區分
    bricks[i].color = (139, 69, 19)  # 棕色

# 選擇 6 個非TNT 的磚塊設為會閃爍的特殊磚塊
non_tnt_indices = [i for i in range(len(bricks)) if not bricks[i].is_tnt]
if len(non_tnt_indices) >= 6:
    blinking_indices = random.sample(non_tnt_indices, 6)
else:
    blinking_indices = non_tnt_indices
for i in blinking_indices:
    bricks[i].is_blinking = True
    # 將基色改為較接近淡藍色，實際顏色由 draw 時 override
    bricks[i].color = bricks[i].base_color


###################### 建立玩家底板 ######################
# 底板設定
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 20
PADDLE_COLOR = (255, 255, 255)  # 白色
PADDLE_SPEED = 10  # 移動速度（像素/幀）- 稍微提高速度以配合球速

# 計算底板的初始位置（螢幕下方中央）
paddle_x = (WIDTH - PADDLE_WIDTH) // 2
paddle_y = HEIGHT - 50  # 距離底部 50 像素

# 建立底板物件
paddle = Paddle(
    paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR, PADDLE_SPEED
)


###################### 建立球 ######################
# 球設定
BALL_RADIUS = 10
BALL_COLOR = (255, 255, 0)  # 黃色
BALL_SPEED = 7  # 移動速度（固定為12）
BALL_MAX_SPEED = 9  # 保留常數，但速度不會改變

# 建立球物件（支援多球）。預設一顆黏在底板上
balls = []
main_ball = Ball(
    paddle.x + paddle.width // 2,
    paddle.y - BALL_RADIUS,
    BALL_RADIUS,
    BALL_COLOR,
    BALL_SPEED,
)
balls.append(main_ball)


###################### 遊戲狀態變數 ######################
game_over = False
score = 0  # 玩家得分
font = pygame.font.Font(None, 36)  # 用於顯示文字的字體

# 爆炸效果相關變數
explosions = []  # 存儲所有正在進行的爆炸效果
# 磚塊碎片 (shards) 與彩蛋 (eggs)
shards = []
eggs = []


class Explosion:
    """爆炸效果類別"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 80
        self.duration = 30  # 爆炸持續幀數
        self.timer = 0

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


###################### 磚塊碎片 (碎片效果) ######################
class Shard:
    """磚塊碎片小方塊，簡單的物理與生命週期"""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        # 初始速度帶有隨機性
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-7.0, -2.0)
        self.size = random.randint(2, 6)
        self.color = color
        self.life = random.randint(40, 80)  # 幀數
        self.timer = 0

    def update(self):
        # 重力
        self.vy += 0.35
        # 空氣阻力
        self.vx *= 0.995
        self.vy *= 0.999
        self.x += self.vx
        self.y += self.vy
        self.timer += 1
        # 邊界外或生命結束就移除
        if self.timer >= self.life or self.y > HEIGHT + 200:
            return False
        return True

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(int(self.x), int(self.y), self.size, self.size),
        )


###################### 彩蛋 (可被撿取) ######################
class Egg:
    """簡單的彩蛋物件，會緩慢下落，碰到板子則觸發撿取效果"""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vy = random.uniform(1.0, 3.0)
        self.radius = 8
        self.collected = False
        # 顏色與裝飾
        self.color = (255, 192, 203)  # 粉紅

    def update(self):
        self.y += self.vy
        # 若落出畫面則刪除
        return not self.collected and self.y < HEIGHT + 100

    def draw(self, surface):
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
            (255, 255, 255),
            (int(self.x) - 3, int(self.y) - self.radius + 2, 6, 4),
        )


###################### 輔助：生成碎片與彩蛋 ######################
def spawn_shards(brick, count=10):
    """從磚塊位置產生碎片"""
    for _ in range(count):
        sx = random.uniform(brick.x, brick.x + brick.width)
        sy = random.uniform(brick.y, brick.y + brick.height)
        # 使用磚塊原色作為碎片顏色
        color = getattr(brick, "base_color", brick.color)
        shards.append(Shard(sx, sy, color))


def spawn_eggs_from_bricks(bricks_list, num_eggs=5):
    """根據剛清完的磚塊清單，產生一些彩蛋。彩蛋生成後會獨立存在，並且不要阻塞下一輪。"""
    available = [b for b in bricks_list]
    if not available:
        return
    # 從被清掉的磚隨機挑一些位置來生成彩蛋；若不足，則在畫面上方隨機生成
    positions = []
    # 優先使用已被打掉的磚的位置（避免使用還沒被打掉的磚）
    dead_bricks = [b for b in bricks_list if b.hit]
    if dead_bricks:
        sample_src = dead_bricks
    else:
        sample_src = bricks_list

    for i in range(num_eggs):
        src = random.choice(sample_src)
        cx = src.x + src.width / 2
        cy = src.y + src.height / 2
        # 把彩蛋稍微往上偏移，讓它看起來從爆炸或碎片處生成
        ex = cx + random.uniform(-20, 20)
        ey = cy + random.uniform(-10, 10)
        # 若該座標在畫面外（例如原本磚塊滑入時的負 y），調整到畫面上方
        if ey < 0:
            ey = random.uniform(20, 80)
            ex = random.uniform(60, WIDTH - 60)
        eggs.append(Egg(ex, ey))


###################### 主迴圈 ######################
# 主迴圈負責：處理事件、更新遊戲狀態、繪製畫面
running = True
while running:
    # 限制為 60 FPS
    clock.tick(60)

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 發射所有仍黏在底板上的球（通常是第一顆）
                for b in balls:
                    if b.stuck:
                        b.launch()
            elif event.key == pygame.K_r and game_over:
                # 重新開始遊戲（僅遊戲結束時）
                game_over = False
                score = 0  # 重置得分
                explosions = []  # 清除爆炸效果
                # 重置所有球回到單一主球
                balls = []
                main_ball = Ball(
                    paddle.x + paddle.width // 2,
                    paddle.y - BALL_RADIUS,
                    BALL_RADIUS,
                    BALL_COLOR,
                    BALL_SPEED,
                )
                balls.append(main_ball)
                # 重置所有磚塊
                bricks = create_new_bricks()

    if not game_over:
        # 處理鍵盤輸入（連續按鍵）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move_left(WIDTH)
        if keys[pygame.K_RIGHT]:
            paddle.move_right(WIDTH)

        # 更新爆炸效果
        explosions = [explosion for explosion in explosions if explosion.update()]

        # 更新所有磚塊（處理 TNT 的閃爍倒數與爆炸）
        now = pygame.time.get_ticks()
        for brick in bricks:
            # 所有磚塊都需要更新（包含下落動畫）
            brick.update(now, bricks)

        # 檢查是否所有磚塊都被摧毀，如果是，先產生彩蛋（從剛清完的磚塊位置）
        # 然後立即進入下一輪（不等待彩蛋被撿取）
        if all(brick.hit for brick in bricks):
            # 原本會在此同時產生彩蛋，但該需求已刪除，僅切換到下一輪
            bricks = create_new_bricks()

        # 更新所有球的位置與碰撞，並移除掉落出界的球
        alive_any = False
        remove_list = []
        for b in balls:
            # update 回傳 False 表示該球落出下方（死亡）
            alive = b.update(paddle, bricks, WIDTH, HEIGHT, balls_list=balls)
            if not alive:
                remove_list.append(b)
            else:
                alive_any = True

        # 移除死亡的球
        for r in remove_list:
            if r in balls:
                balls.remove(r)

        # 若沒有任何球存活，遊戲結束
        if not alive_any:
            game_over = True

        # 更新碎片
        shards = [s for s in shards if s.update()]

        # 更新彩蛋並檢查是否被撿取（碰到底板）
        remaining_eggs = []
        for egg in eggs:
            alive = egg.update()
            if not alive:
                continue
            # 檢查與底板的簡單碰撞
            if (
                egg.y + egg.radius >= paddle.y
                and egg.x >= paddle.x
                and egg.x <= paddle.x + paddle.width
            ):
                # 撿取效果：加分並標記為收集
                egg.collected = True
                score += 250
                # 可在這裡加入其他強化效果（例如加寬底板）
                continue
            remaining_eggs.append(egg)
        eggs = remaining_eggs

    # 繪製：先清空背景
    screen.fill((0, 0, 0))  # 黑色背景

    if not game_over:
        # 繪製所有磚塊
        for b in bricks:
            b.draw(screen)

        # 繪製玩家底板
        paddle.draw(screen)

        # 繪製所有球
        for b in balls:
            b.draw(screen)

        # 繪製碎片
        for s in shards:
            s.draw(screen)

        # 繪製彩蛋
        for e in eggs:
            e.draw(screen)

        # 繪製爆炸效果
        for explosion in explosions:
            explosion.draw(screen)

        # 在右上角顯示得分
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect()
        score_rect.topright = (WIDTH - 10, 10)
        screen.blit(score_text, score_rect)
    else:
        # 遊戲結束畫面
        font_large = pygame.font.Font(None, 74)
        text = font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(text, text_rect)

        # 顯示最終得分
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(score_text, score_rect)

        restart_text = font.render("Press R to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    # 若遊戲開始時，顯示提示訊息
    # 若有任何球還黏在底板上且遊戲未結束，顯示提示
    any_stuck = any(b.stuck for b in balls)
    if any_stuck and not game_over:
        text = font.render("Press UP to launch ball", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(text, text_rect)

    # 將緩衝畫面更新到顯示器
    pygame.display.flip()

# 離開前清理 Pygame
pygame.quit()
sys.exit()
