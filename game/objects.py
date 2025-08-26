# -*- coding: utf-8 -*-
"""
遊戲物件類別模組

包含敲磚塊遊戲中的所有主要物件類別：磚塊、底板、球。
"""

######################載入套件######################
import pygame
import math
import random
from collections import deque

######################導入設定######################
from config import (
    BRICK_CONFIG,
    PADDLE_CONFIG,
    BALL_CONFIG,
    TNT_CONFIG,
    BLINKING_CONFIG,
    SCORE_CONFIG,
    COLORS,
    PHYSICS_CONFIG,
)


######################物件類別######################


class Brick:
    """
    代表一個磚塊的類別\n
    \n
    磚塊是玩家要打破的目標物件，具有以下特性：\n
    1. 普通磚塊：被球擊中後會消失並給分\n
    2. TNT 磚塊：被擊中後會閃爍倒數，然後爆炸影響周圍磚塊\n
    3. 閃爍磚塊：會持續改變顏色，被擊中後會產生額外的球\n
    \n
    屬性:\n
    x, y (int): 磚塊左上角座標\n
    width, height (int): 磚塊的尺寸\n
    color (tuple): 當前顯示的顏色 (R, G, B)\n
    base_color (tuple): 原始顏色，用於重置\n
    hit (bool): 是否已被擊中並需要移除\n
    is_tnt (bool): 是否為 TNT 爆炸磚塊\n
    is_blinking (bool): 是否為會閃爍的特殊磚塊\n
    falling (bool): 是否正在執行下落動畫\n
    \n
    TNT 相關屬性:\n
    tnt_primed (bool): TNT 是否已被觸發開始倒數\n
    tnt_primed_start (int): TNT 開始倒數的時間戳記\n
    \n
    使用範例:\n
    brick = Brick(100, 50, is_tnt=True)  # 創建一個 TNT 磚塊\n
    brick.draw(screen)  # 繪製磚塊\n
    brick.start_priming()  # 觸發 TNT 倒數\n
    """

    def __init__(self, x, y, width=None, height=None, color=None, is_tnt=False):
        """
        初始化磚塊物件\n
        \n
        參數:\n
        x (int): 磚塊左上角 X 座標，範圍 0 到視窗寬度\n
        y (int): 磚塊左上角 Y 座標，範圍 0 到視窗高度\n
        width (int): 磚塊寬度，預設使用設定檔中的值\n
        height (int): 磚塊高度，預設使用設定檔中的值\n
        color (tuple): 磚塊顏色 (R, G, B)，預設為番茄紅\n
        is_tnt (bool): 是否為 TNT 磚塊，預設為 False\n
        """
        # 設定磚塊在螢幕上的位置
        self.x = x
        self.y = y

        # 設定磚塊的大小，如果沒指定就用設定檔的預設值
        self.width = width or BRICK_CONFIG["WIDTH"]
        self.height = height or BRICK_CONFIG["HEIGHT"]

        # 設定磚塊的顏色
        self.color = color or COLORS["BRICK_TOMATO"]
        self.base_color = self.color  # 保存原始顏色，用於重置顏色效果

        # 磚塊的狀態
        self.hit = False  # 是否被球打中了
        self.is_tnt = is_tnt  # 是否是會爆炸的 TNT 磚塊

        # TNT 爆炸相關的狀態
        self.tnt_primed = False  # TNT 是否已經被觸發開始倒數
        self.tnt_primed_start = 0  # 開始倒數的時間點
        self.tnt_primed_cycles = 0  # 已經閃爍了幾次
        # 從設定檔讀取 TNT 的倒數時間設定
        self.tnt_blink_duration = TNT_CONFIG["BLINK_DURATION"]
        self.tnt_blink_repeats = TNT_CONFIG["BLINK_REPEATS"]

        # 特殊閃爍磚塊的設定
        self.is_blinking = False  # 是否是會持續閃爍變色的特殊磚塊
        self.blink_period = BLINKING_CONFIG["PERIOD"]  # 顏色變化的週期
        self.blink_offset = random.randint(0, 1000)  # 隨機偏移，讓每個磚塊閃爍不同步

        # 磚塊下落動畫相關
        self.falling = False  # 是否正在下落
        self.target_y = y  # 目標 Y 座標
        self.fall_speed = PHYSICS_CONFIG["FALL_SPEED"]  # 下落速度

    def draw(self, surface):
        """
        在螢幕上繪製磚塊\n
        \n
        根據磚塊的狀態繪製不同的視覺效果：\n
        1. 普通磚塊：顯示基本顏色\n
        2. 閃爍磚塊：在調色盤中的顏色間漸變\n
        3. TNT 倒數中：紅白交替閃爍\n
        4. TNT 磚塊：顯示 "TNT" 文字\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 如果磚塊已經被打掉了，就不用畫了
        if not self.hit:
            draw_color = self.color  # 預設使用磚塊的基本顏色

            # 如果是會閃爍的特殊磚塊，要計算當前應該顯示什麼顏色
            if self.is_blinking:
                palette = COLORS["BLINK_PALETTE"]  # 顏色調色盤
                # 根據時間計算顏色變化的進度
                t = (pygame.time.get_ticks() + self.blink_offset) % self.blink_period
                factor = (math.sin(2 * math.pi * (t / self.blink_period)) * 0.5) + 0.5

                # 在調色盤的多個顏色間做平滑漸變
                segs = len(palette) - 1
                scaled = factor * segs
                idx = int(scaled)
                frac = scaled - idx
                idx = max(0, min(idx, segs - 1))
                c1 = palette[idx]
                c2 = palette[min(idx + 1, segs)]
                # 計算兩個顏色間的漸變色
                draw_color = (
                    int(c1[0] * (1 - frac) + c2[0] * frac),
                    int(c1[1] * (1 - frac) + c2[1] * frac),
                    int(c1[2] * (1 - frac) + c2[2] * frac),
                )

            # 如果是正在倒數的 TNT，要顯示紅白閃爍警告
            if self.is_tnt and self.tnt_primed and not self.hit:
                t = pygame.time.get_ticks() - self.tnt_primed_start
                period = self.tnt_blink_duration * 2
                phase = (t % period) < self.tnt_blink_duration
                # 紅色和白色交替閃爍，讓玩家知道要爆炸了
                draw_color = COLORS["RED"] if phase else COLORS["WHITE"]

            # 畫出磚塊的矩形
            pygame.draw.rect(
                surface,
                draw_color,
                pygame.Rect(self.x, self.y, self.width, self.height),
            )

            # 如果是 TNT 磚塊，在上面寫 "TNT" 字樣讓玩家知道
            if self.is_tnt:
                from config import FONT_CONFIG

                font = pygame.font.Font(None, FONT_CONFIG["TNT_TEXT_SIZE"])
                text = font.render("TNT", True, COLORS["WHITE"])
                text_rect = text.get_rect(
                    center=(self.x + self.width // 2, self.y + self.height // 2)
                )
                surface.blit(text, text_rect)

    def start_priming(self):
        """
        啟動 TNT 磚塊的倒數程序\n
        \n
        當球撞到 TNT 磚塊時呼叫此方法，開始紅白閃爍倒數。\n
        倒數結束後會觸發爆炸，炸掉周圍範圍內的所有磚塊。\n
        \n
        安全檢查:\n
        - 只有 TNT 磚塊才能被觸發\n
        - 已經在倒數中的 TNT 不會重複觸發\n
        - 已經被摧毀的磚塊不會被觸發\n
        """
        # 檢查是否為 TNT 磚塊，不是的話就直接返回
        if not self.is_tnt:
            return
        # 檢查是否已經在倒數中或已經被摧毀
        if self.tnt_primed or self.hit:
            return

        # 開始 TNT 倒數程序
        self.tnt_primed = True
        self.tnt_primed_start = pygame.time.get_ticks()  # 記錄開始倒數的時間
        self.tnt_primed_cycles = 0  # 重置閃爍次數計數器

    def update(self, now, all_bricks):
        """
        每一幀更新磚塊的狀態\n
        \n
        處理兩種動畫效果：\n
        1. 磚塊下落動畫：新關卡時磚塊從上方滑下來的效果\n
        2. TNT 倒數檢查：檢查 TNT 是否倒數完畢該爆炸了\n
        \n
        參數:\n
        now (int): 當前時間戳記（毫秒）\n
        all_bricks (list): 所有磚塊的列表，用於 TNT 爆炸處理\n
        """
        # 處理磚塊下落動畫
        if self.falling:
            # 如果還沒到達目標位置就繼續下落
            if self.y < self.target_y:
                self.y += self.fall_speed
                # 如果已經到達或超過目標位置，就停止下落
                if self.y >= self.target_y:
                    self.y = self.target_y
                    self.falling = False

        # 處理 TNT 倒數和爆炸
        # 只處理還沒被摧毀且已經開始倒數的 TNT
        if self.is_tnt and self.tnt_primed and not self.hit:
            elapsed = now - self.tnt_primed_start  # 計算已經倒數多長時間
            one_cycle = self.tnt_blink_duration * 2  # 一次完整閃爍的時間
            cycles_completed = elapsed // one_cycle  # 已經完成幾次閃爍

            # 如果閃爍次數達到設定值，就該爆炸了
            if cycles_completed >= self.tnt_blink_repeats:
                # 匯入爆炸處理函數並執行爆炸
                from .utils import explode_tnt

                explode_tnt(self, all_bricks)
                self.tnt_primed = False  # 爆炸後重置倒數狀態
            else:
                # 更新已完成的閃爍次數
                self.tnt_primed_cycles = cycles_completed


class Paddle:
    """
    代表玩家控制的底板\n
    \n
    底板是玩家用來接球和控制球反彈方向的工具。\n
    玩家可以用左右箭頭鍵或 A、D 鍵來移動底板。\n
    \n
    特性:\n
    1. 可以左右移動，但不能超出螢幕邊界\n
    2. 球撞到底板不同位置會有不同的反彈角度\n
    3. 撞到底板邊緣會讓球彈得更斜\n
    \n
    屬性:\n
    x, y (int): 底板左上角座標\n
    width, height (int): 底板的尺寸\n
    color (tuple): 底板顏色 (R, G, B)\n
    speed (int): 移動速度（每次按鍵移動的像素數）\n
    \n
    使用範例:\n
    paddle = Paddle(350, 550)  # 在螢幕下方中央創建底板\n
    paddle.move_left(800)      # 向左移動，不超出螢幕寬度\n
    paddle.draw(screen)        # 繪製底板\n
    """

    def __init__(self, x, y, width=None, height=None, color=None, speed=None):
        """
        初始化底板物件\n
        \n
        參數:\n
        x (int): 底板左上角 X 座標\n
        y (int): 底板左上角 Y 座標\n
        width (int): 底板寬度，預設使用設定檔中的值\n
        height (int): 底板高度，預設使用設定檔中的值\n
        color (tuple): 底板顏色 (R, G, B)，預設為白色\n
        speed (int): 移動速度，預設使用設定檔中的值\n
        """
        # 設定底板在螢幕上的位置
        self.x = x
        self.y = y

        # 設定底板的大小，如果沒指定就用設定檔的預設值
        self.width = width or PADDLE_CONFIG["WIDTH"]
        self.height = height or PADDLE_CONFIG["HEIGHT"]

        # 設定底板的外觀和移動速度
        self.color = color or PADDLE_CONFIG["COLOR"]
        self.speed = speed or PADDLE_CONFIG["SPEED"]

    def move_left(self, screen_width):
        """
        向左移動底板\n
        \n
        底板會向左移動一個速度單位的距離，\n
        但不會超出螢幕的左邊界。\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度，用於邊界檢查\n
        """
        # 向左移動指定的速度距離
        self.x -= self.speed
        # 檢查是否超出左邊界，如果超出就設定在邊界上
        if self.x < 0:
            self.x = 0

    def move_right(self, screen_width):
        """
        向右移動底板\n
        \n
        底板會向右移動一個速度單位的距離，\n
        但不會超出螢幕的右邊界。\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度，用於邊界檢查\n
        """
        # 向右移動指定的速度距離
        self.x += self.speed
        # 檢查是否超出右邊界，如果超出就設定在邊界上
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width

    def draw(self, surface):
        """
        在螢幕上繪製底板\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 畫出底板的矩形
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(self.x, self.y, self.width, self.height),
        )


class Ball:
    """
    代表遊戲中的彈跳球\n
    \n
    球是遊戲的核心物件，負責在螢幕中彈跳並擊破磚塊。\n
    球具有複雜的物理行為和碰撞檢測系統。\n
    \n
    特性:\n
    1. 會與螢幕邊界、底板、磚塊發生碰撞並反彈\n
    2. 剛開始會黏在底板上，按上鍵後發射\n
    3. 撞到底板不同位置會以不同角度反彈\n
    4. 撞到磚塊會產生不同的特殊效果\n
    5. 掉到螢幕底部會導致遊戲結束\n
    \n
    屬性:\n
    x, y (float): 球的中心座標\n
    radius (int): 球的半徑\n
    color (tuple): 球的顏色 (R, G, B)\n
    speed (float): 球的移動速度\n
    vx, vy (float): 球在 X 和 Y 方向的速度分量\n
    stuck (bool): 是否黏在底板上等待發射\n
    \n
    特殊狀態:\n
    spinning (bool): 是否正在執行勝利繞圈動畫\n
    \n
    使用範例:\n
    ball = Ball(400, 300)  # 在螢幕中央創建球\n
    ball.launch()          # 發射球\n
    success = ball.update(paddle, bricks, 800, 600)  # 更新並檢查碰撞\n
    """

    def __init__(self, x, y, radius=None, color=None, speed=None):
        """
        初始化球物件\n
        \n
        參數:\n
        x (float): 球的中心 X 座標\n
        y (float): 球的中心 Y 座標\n
        radius (int): 球的半徑，預設使用設定檔中的值\n
        color (tuple): 球的顏色 (R, G, B)，預設為黃色\n
        speed (float): 球的移動速度，預設使用設定檔中的值\n
        """
        # 設定球在螢幕上的位置（中心點座標）
        self.x = x
        self.y = y

        # 設定球的外觀，如果沒指定就用設定檔的預設值
        self.radius = radius or BALL_CONFIG["RADIUS"]
        self.color = color or BALL_CONFIG["COLOR"]

        # 設定球的移動相關屬性
        self.speed = speed or BALL_CONFIG["SPEED"]
        self.vx = 0  # X 方向的速度分量
        self.vy = 0  # Y 方向的速度分量

        # 遊戲開始時球要黏在底板上等待玩家發射
        self.stuck = True

        # 勝利時的繞圈動畫相關參數
        self.spinning = False  # 是否正在繞圈
        self.spin_center_x = 0  # 繞圈的中心點 X 座標
        self.spin_center_y = 0  # 繞圈的中心點 Y 座標
        self.spin_radius = 0  # 繞圈的半徑
        self.spin_angle = 0.0  # 當前的角度位置
        self.spin_angular_speed = 0.15  # 繞圈的角速度

    def update(
        self,
        paddle,
        bricks,
        screen_width,
        screen_height,
        balls_list=None,
        game_state=None,
    ):
        """
        統一的球更新方法 - 處理球的移動和所有碰撞檢測\n
        \n
        此方法是球物理引擎的核心，按順序處理：\n
        1. 黏在底板狀態的跟隨移動\n
        2. 球的位置更新\n
        3. 與螢幕邊界的碰撞\n
        4. 與底板的碰撞（包含角度計算）\n
        5. 與磚塊的碰撞（包含特殊效果觸發）\n
        \n
        參數:\n
        paddle (Paddle): 底板物件，包含位置和尺寸資訊\n
        bricks (list): 磚塊陣列，包含所有未被擊中的磚塊\n
        screen_width (int): 螢幕寬度，範圍 > 0\n
        screen_height (int): 螢幕高度，範圍 > 0\n
        balls_list (list): 球的陣列，用於新增額外球\n
        game_state (GameState): 遊戲狀態物件，用於更新分數和特效\n
        \n
        回傳:\n
        bool: True 表示球仍然存活，False 表示球掉出螢幕底部\n
        \n
        物理算法說明:\n
        - 底板碰撞：根據撞擊位置計算反彈角度，邊緣反彈更斜\n
        - 磚塊碰撞：比較撞擊位置決定水平或垂直反彈\n
        - 速度保持：碰撞後重新正規化速度以保持恆定速率\n
        """
        # 如果球還黏在底板上，就跟著底板一起移動
        if self.stuck:
            # 球的位置設定在底板正中央的上方
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - self.radius
            return True  # 黏在底板上的球不會死亡

        # 根據當前速度更新球的位置
        self.x += self.vx
        self.y += self.vy

        # 檢查球是否撞到左右邊界
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            # 水平方向速度反轉（彈回來）
            self.vx = -self.vx
            # 確保球不會卡在邊界外面
            if self.x - self.radius <= 0:
                self.x = self.radius  # 貼著左邊界
            else:
                self.x = screen_width - self.radius  # 貼著右邊界
            # 重新正規化速度，保持速度大小不變
            self.normalize_velocity()

        # 檢查球是否撞到上邊界
        if self.y - self.radius <= 0:
            # 垂直方向速度反轉（向下彈）
            self.vy = -self.vy
            self.y = self.radius  # 確保球不會卡在上邊界外面
            self.normalize_velocity()

        # 檢查球是否掉到螢幕底部（遊戲結束條件）
        if self.y + self.radius >= screen_height:
            return False  # 回傳 False 表示這顆球死亡了

        # 檢查球是否撞到底板
        if (
            self.y + self.radius >= paddle.y  # 球的底部觸碰到底板頂部
            and self.y - self.radius
            <= paddle.y + paddle.height  # 球的頂部還在底板底部之上
            and self.x >= paddle.x  # 球的中心在底板左邊界右側
            and self.x <= paddle.x + paddle.width  # 球的中心在底板右邊界左側
        ):
            # 計算球撞到底板的相對位置（-1 到 1 之間）
            # 0 表示撞到正中央，-1 表示撞到最左邊，1 表示撞到最右邊
            hit_pos = (self.x - paddle.x) / paddle.width

            # 根據撞擊位置計算反彈角度
            # 撞到邊緣會讓球彈得更斜，增加遊戲趣味性
            max_angle = math.radians(PHYSICS_CONFIG["BOUNCE_ANGLE_MAX"])
            angle = (hit_pos - 0.5) * 2 * max_angle

            # 根據計算出的角度設定新的速度分量
            self.vx = self.speed * math.sin(angle)  # 水平速度（左右）
            self.vy = -self.speed * math.cos(angle)  # 垂直速度（必須向上）

            # 確保球不會卡在底板裡面
            self.y = paddle.y - self.radius

        # 檢查球是否撞到任何磚塊
        for brick in bricks:
            # 只檢查還沒被打掉的磚塊
            if not brick.hit and self.check_brick_collision(brick):
                # 根據磚塊類型執行不同的處理
                if brick.is_tnt:
                    # 如果撞到 TNT 磚塊，啟動倒數程序（不會立即摧毀）
                    brick.start_priming()
                else:
                    # 普通磚塊直接摧毀
                    brick.hit = True

                    # 產生磚塊碎片效果讓畫面更生動
                    if game_state:
                        try:
                            from .effects import Shard

                            count = 8  # 每個磚塊產生 8 個碎片
                            for _ in range(count):
                                # 在磚塊範圍內隨機產生碎片位置
                                sx = random.uniform(brick.x, brick.x + brick.width)
                                sy = random.uniform(brick.y, brick.y + brick.height)
                                # 使用磚塊的原始顏色作為碎片顏色
                                color = getattr(brick, "base_color", brick.color)
                                game_state.shards.append(Shard(sx, sy, color))
                        except Exception:
                            # 如果特效載入失敗也不影響遊戲運行
                            pass

                    # 增加玩家得分
                    if game_state:
                        game_state.score += SCORE_CONFIG["BRICK_HIT"]

                # 如果撞到會閃爍的特殊磚塊，產生額外的球
                if brick.is_blinking and balls_list is not None:
                    for _ in range(BLINKING_CONFIG["EXTRA_BALLS"]):
                        # 創建新球，位置和當前球相同
                        new_ball = Ball(
                            self.x, self.y, self.radius, self.color, self.speed
                        )
                        new_ball.stuck = False  # 新球直接開始移動

                        # 給新球隨機的移動方向
                        angle = random.uniform(-math.pi, math.pi)
                        new_ball.vx = math.cos(angle) * new_ball.speed
                        new_ball.vy = math.sin(angle) * new_ball.speed
                        balls_list.append(new_ball)

                # 處理球的反彈（簡單的反彈邏輯）
                # 根據球撞到磚塊的哪一側來決定反彈方向
                if self.x < brick.x or self.x > brick.x + brick.width:
                    # 撞到磚塊的左側或右側，水平速度反轉
                    self.vx = -self.vx
                if self.y < brick.y or self.y > brick.y + brick.height:
                    # 撞到磚塊的上方或下方，垂直速度反轉
                    self.vy = -self.vy

                # 重新正規化速度，確保球的速度大小保持恆定
                angle = math.atan2(self.vy, self.vx)
                self.vx = math.cos(angle) * self.speed
                self.vy = math.sin(angle) * self.speed

                # 一次只處理一個磚塊碰撞，避免複雜的多重碰撞問題
                break

        # 回傳 True 表示球仍然存活
        return True

    def check_brick_collision(self, brick):
        """
        檢查球是否與指定磚塊發生碰撞\n
        \n
        使用圓形與矩形的碰撞檢測算法：\n
        1. 找出矩形上離圓心最近的點\n
        2. 計算該點與圓心的距離\n
        3. 如果距離小於圓的半徑就表示碰撞\n
        \n
        參數:\n
        brick (Brick): 要檢查碰撞的磚塊物件\n
        \n
        回傳:\n
        bool: True 表示發生碰撞，False 表示沒有碰撞\n
        \n
        算法說明:\n
        使用點到矩形的最短距離來判斷圓形碰撞，\n
        這比簡單的邊界框碰撞更精確。\n
        """
        # 找出磚塊矩形上離球心最近的點
        closest_x = max(brick.x, min(self.x, brick.x + brick.width))
        closest_y = max(brick.y, min(self.y, brick.y + brick.height))

        # 計算球心到最近點的距離
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y

        # 如果距離小於球的半徑就表示碰撞了
        return distance_squared < (self.radius * self.radius)

    def launch(self):
        """
        發射球（當玩家按上鍵時呼叫）\n
        \n
        將球從黏在底板的狀態改為自由移動狀態，\n
        並給球一個向上的初始速度。\n
        """
        if self.stuck:
            self.stuck = False  # 解除黏在底板的狀態
            self.vx = 0  # 水平速度為 0（直直向上）
            self.vy = -self.speed  # 垂直速度向上（負數表示向上）

    def start_spin(self, center_x, center_y, radius=80):
        """
        開始勝利繞圈動畫\n
        \n
        遊戲勝利時讓球繞著指定點做圓周運動，\n
        創造慶祝的視覺效果。\n
        \n
        參數:\n
        center_x (float): 繞圈中心點的 X 座標\n
        center_y (float): 繞圈中心點的 Y 座標\n
        radius (float): 繞圈的半徑，預設為 80 像素\n
        """
        self.spinning = True
        self.spin_center_x = center_x
        self.spin_center_y = center_y
        self.spin_radius = radius
        # 計算球當前位置相對於中心點的角度
        self.spin_angle = math.atan2(self.y - center_y, self.x - center_x)
        self.spin_angular_speed = 0.12  # 繞圈的角速度

    def update_spin(self):
        """
        更新繞圈動畫的位置\n
        \n
        每一幀都會呼叫此方法來更新球在圓周上的位置，\n
        讓球持續繞圈移動。\n
        """
        if not self.spinning:
            return

        # 更新角度位置
        self.spin_angle += self.spin_angular_speed

        # 根據新角度計算球的位置
        self.x = self.spin_center_x + math.cos(self.spin_angle) * self.spin_radius
        self.y = self.spin_center_y + math.sin(self.spin_angle) * self.spin_radius

    def draw(self, surface):
        """
        在螢幕上繪製球\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 畫出圓形的球，座標要轉換成整數
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def normalize_velocity(self):
        """
        重新正規化球的速度向量\n
        \n
        確保球的速度大小保持恆定，避免因為碰撞計算\n
        導致球越來越快或越來越慢的問題。\n
        \n
        算法說明:\n
        1. 計算當前速度向量的大小\n
        2. 如果速度為 0 就設定為向上移動\n
        3. 將速度向量正規化到設定的速度大小\n
        """
        # 計算當前速度向量的大小
        mag = math.hypot(self.vx, self.vy)

        # 如果速度為 0（不應該發生，但保險起見）
        if mag == 0:
            self.vx = 0
            self.vy = -self.speed  # 設定為向上移動
            return

        # 將速度向量正規化到設定的速度大小
        self.vx = (self.vx / mag) * self.speed
        self.vy = (self.vy / mag) * self.speed
