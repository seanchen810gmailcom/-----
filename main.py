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
        # 被擊中狀態
        self.hit = False
        # 是否為TNT磚塊
        self.is_tnt = is_tnt

    def draw(self, surface):
        """在傳入的 surface 上繪製磚塊（若尚未被擊中）。"""
        if not self.hit:
            pygame.draw.rect(
                surface,
                self.color,
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


###################### TNT爆炸函數 ######################
def explode_tnt(tnt_brick, all_bricks):
    """處理TNT磚塊爆炸，炸掉周圍的磚塊。

    參數：
    - tnt_brick: 被擊中的TNT磚塊
    - all_bricks: 所有磚塊的列表

    返回：
    - 被炸掉的磚塊數量
    """
    exploded_count = 0
    explosion_radius = 100  # 爆炸半徑（像素）

    # TNT磚塊的中心點
    tnt_center_x = tnt_brick.x + tnt_brick.width // 2
    tnt_center_y = tnt_brick.y + tnt_brick.height // 2

    for brick in all_bricks:
        if not brick.hit:  # 只檢查還沒被擊中的磚塊
            # 計算磚塊中心點
            brick_center_x = brick.x + brick.width // 2
            brick_center_y = brick.y + brick.height // 2

            # 計算距離
            distance = math.sqrt(
                (tnt_center_x - brick_center_x) ** 2
                + (tnt_center_y - brick_center_y) ** 2
            )

            # 如果在爆炸範圍內，炸掉這個磚塊
            if distance <= explosion_radius:
                brick.hit = True
                exploded_count += 1

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

    def update(self, paddle, bricks, screen_width, screen_height):
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
                brick.hit = True

                # 如果撞到的是TNT磚塊，觸發爆炸
                if brick.is_tnt:
                    explode_tnt(brick, bricks)

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
        bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color))

# 隨機選擇5個磚塊設為TNT磚塊
tnt_indices = random.sample(range(len(bricks)), 5)
for i in tnt_indices:
    bricks[i].is_tnt = True
    # TNT磚塊使用較暗的顏色以便區分
    bricks[i].color = (139, 69, 19)  # 棕色


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
BALL_SPEED = 12  # 移動速度（固定為12）
BALL_MAX_SPEED = 12  # 保留常數，但速度不會改變

# 建立球物件（初始位置會在update中設定為黏在底板上）
ball = Ball(
    paddle.x + paddle.width // 2,
    paddle.y - BALL_RADIUS,
    BALL_RADIUS,
    BALL_COLOR,
    BALL_SPEED,
)


###################### 遊戲狀態變數 ######################
game_over = False


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
            if event.key == pygame.K_UP and ball.stuck:
                ball.launch()  # 發射球
            elif event.key == pygame.K_r and (
                game_over or all(brick.hit for brick in bricks)
            ):
                # 重新開始遊戲（遊戲結束或勝利時）
                game_over = False
                ball.stuck = True
                ball.vx = 0
                ball.vy = 0
                # 停止繞圈並重置速度
                ball.spinning = False
                ball.speed = BALL_SPEED
                # 重置所有磚塊
                for brick in bricks:
                    brick.hit = False
                    brick.is_tnt = False
                    # 重置顏色到原始顏色
                    row = (brick.y - BRICK_MARGIN_TOP) // (
                        BRICK_HEIGHT + BRICK_SPACING_Y
                    )
                    brick.color = row_colors[row % len(row_colors)]

                # 重新隨機選擇5個磚塊設為TNT磚塊
                tnt_indices = random.sample(range(len(bricks)), 5)
                for i in tnt_indices:
                    bricks[i].is_tnt = True
                    # TNT磚塊使用較暗的顏色以便區分
                    bricks[i].color = (139, 69, 19)  # 棕色

    if not game_over:
        # 處理鍵盤輸入（連續按鍵）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move_left(WIDTH)
        if keys[pygame.K_RIGHT]:
            paddle.move_right(WIDTH)

        # 更新球的位置和碰撞檢測
        if not ball.update(paddle, bricks, WIDTH, HEIGHT):
            game_over = True

    # 繪製：先清空背景
    screen.fill((0, 0, 0))  # 黑色背景

    if not game_over:
        # 繪製所有磚塊
        for b in bricks:
            b.draw(screen)

        # 繪製玩家底板
        paddle.draw(screen)

        # 若已勝利並開始繞圈，更新並繪製繞圈位置；否則正常繪製球
        all_bricks_hit = all(brick.hit for brick in bricks)
        if all_bricks_hit:
            # 顯示勝利訊息
            font = pygame.font.Font(None, 74)
            text = font.render("YOU WIN!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

            restart_text = pygame.font.Font(None, 36).render(
                "Press R to restart", True, (255, 255, 255)
            )
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)

            # 若還沒開始繞圈就啟動
            if not ball.spinning:
                # 讓球繞在 "YOU WIN" 文字中央附近
                win_center_x = WIDTH // 2
                win_center_y = HEIGHT // 2
                ball.start_spin(win_center_x, win_center_y, radius=100)

            # 每幀更新繞圈位置並繪製球
            ball.update_spin()
            ball.draw(screen)
        else:
            # 正常繪製球
            ball.draw(screen)
        # end if all_bricks_hit
    else:
        # 遊戲結束畫面
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

        restart_text = pygame.font.Font(None, 36).render(
            "Press R to restart", True, (255, 255, 255)
        )
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    # 若遊戲開始時，顯示提示訊息
    if ball.stuck and not game_over:
        font = pygame.font.Font(None, 36)
        text = font.render("Press UP to launch ball", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(text, text_rect)

    # 將緩衝畫面更新到顯示器
    pygame.display.flip()

# 離開前清理 Pygame
pygame.quit()
sys.exit()
