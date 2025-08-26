# -*- coding: utf-8 -*-
"""
遊戲邏輯模組

包含遊戲狀態管理、得分系統、遊戲流程控制等核心邏輯。
"""

######################載入套件######################
import pygame

######################導入設定######################
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PADDLE_CONFIG,
    BALL_CONFIG,
    FONT_CONFIG,
    COLORS,
    SCORE_CONFIG,
)

######################導入遊戲物件######################
from .objects import Paddle, Ball
from .utils import initialize_bricks, create_new_bricks


######################物件類別######################


class GameState:
    """
    遊戲狀態管理類別\n
    \n
    負責管理整個遊戲的狀態和流程，包含：\n
    1. 遊戲物件的創建和管理（磚塊、球、底板）\n
    2. 分數和關卡系統\n
    3. 使用者輸入處理\n
    4. 遊戲邏輯更新\n
    5. 遊戲結束判定\n
    \n
    屬性:\n
    score (int): 玩家當前分數\n
    level (int): 當前關卡數\n
    state (str): 遊戲狀態 ("PLAYING", "GAME_OVER")\n
    game_over (bool): 是否遊戲結束\n
    running (bool): 是否繼續運行遊戲\n
    \n
    遊戲物件:\n
    bricks (list): 所有磚塊的列表\n
    paddle (Paddle): 玩家控制的底板\n
    balls (list): 所有球的列表\n
    \n
    特效物件:\n
    explosions (list): 爆炸效果列表\n
    shards (list): 碎片效果列表\n
    eggs (list): 彩蛋物件列表\n
    \n
    使用範例:\n
    game_state = GameState()  # 創建遊戲狀態\n
    game_state.handle_events(event)  # 處理事件\n
    game_state.update()  # 更新遊戲邏輯\n
    game_state.draw(screen)  # 繪製遊戲畫面\n
    """

    def __init__(self):
        """
        初始化遊戲狀態\n
        \n
        設定遊戲的初始狀態，創建必要的字體物件，\n
        並呼叫 reset_game() 來初始化所有遊戲物件。\n
        """
        # 遊戲統計資訊
        self.score = 0  # 玩家得分
        self.level = 1  # 當前關卡
        self.tnt_count = 0  # TNT 爆炸計數（統計用）

        # 遊戲狀態控制
        self.state = "PLAYING"  # 遊戲狀態
        self.game_over = False  # 是否遊戲結束
        self.running = True  # 是否繼續運行

        # 載入遊戲字體，用於顯示文字資訊
        self.font = pygame.font.Font(None, FONT_CONFIG["DEFAULT_SIZE"])
        self.font_large = pygame.font.Font(None, FONT_CONFIG["LARGE_SIZE"])

        # 初始化所有遊戲物件
        self.reset_game()

    def reset_game(self):
        """
        重置遊戲到初始狀態\n
        \n
        當遊戲開始或玩家選擇重新開始時呼叫。\n
        清除所有遊戲物件並重新創建到初始狀態。\n
        \n
        重置內容:\n
        1. 遊戲狀態標誌\n
        2. 分數和關卡\n
        3. 磚塊陣列\n
        4. 底板位置\n
        5. 球的狀態\n
        6. 所有特效物件\n
        """
        # 重置遊戲狀態標誌
        self.game_over = False
        self.state = "PLAYING"

        # 重置遊戲統計數據
        self.score = 0
        self.level = 1
        self.tnt_count = 0

        # 重新創建磚塊陣列
        self.bricks = initialize_bricks()

        # 重新創建底板，位置在螢幕下方中央
        paddle_x = (WINDOW_WIDTH - PADDLE_CONFIG["WIDTH"]) // 2
        paddle_y = WINDOW_HEIGHT - PADDLE_CONFIG["MARGIN_BOTTOM"]
        self.paddle = Paddle(paddle_x, paddle_y)

        # 重新創建球，一開始只有一顆球黏在底板上
        self.balls = []
        main_ball = Ball(
            self.paddle.x + self.paddle.width // 2,  # 球在底板中央
            self.paddle.y - BALL_CONFIG["RADIUS"],  # 球在底板上方
        )
        self.balls.append(main_ball)

        # 清空所有特效物件
        self.explosions = []  # 爆炸效果
        self.shards = []  # 磚塊碎片
        self.eggs = []  # 彩蛋物件

    def handle_events(self, event):
        """
        處理使用者輸入事件\n
        \n
        響應玩家的各種按鍵操作，包含遊戲控制和狀態轉換。\n
        \n
        支援的按鍵:\n
        - UP 鍵: 發射黏在底板上的球\n
        - R 鍵: 遊戲結束時重新開始\n
        - ESC 鍵: 退出遊戲\n
        \n
        參數:\n
        event (pygame.event.Event): Pygame 事件物件\n
        """
        if event.type == pygame.QUIT:
            # 玩家點了視窗的關閉按鈕
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 按上鍵發射所有還黏在底板上的球
                for ball in self.balls:
                    if ball.stuck:
                        ball.launch()
            elif event.key == pygame.K_r and (
                self.game_over or self.state == "GAME_OVER"
            ):
                # 遊戲結束時按 R 鍵重新開始
                self.reset_game()
            elif event.key == pygame.K_ESCAPE:
                # 按 ESC 鍵退出遊戲
                self.running = False

    def handle_continuous_input(self):
        """
        處理連續按鍵輸入（底板移動）\n
        \n
        檢查玩家是否持續按住方向鍵來移動底板。\n
        這種輸入需要每一幀都檢查，而不是只在按下時觸發一次。\n
        \n
        支援的按鍵:\n
        - 左箭頭或 A 鍵: 向左移動底板\n
        - 右箭頭或 D 鍵: 向右移動底板\n
        """
        # 只有在遊戲進行中才處理移動
        if not self.game_over:
            keys = pygame.key.get_pressed()  # 獲取當前所有按鍵的狀態
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                # 向左移動底板
                self.paddle.move_left(WINDOW_WIDTH)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                # 向右移動底板
                self.paddle.move_right(WINDOW_WIDTH)

    def update(self):
        """更新遊戲狀態"""
        # 如果遊戲結束，不更新遊戲邏輯
        if self.game_over:
            return

        # 處理連續輸入
        self.handle_continuous_input()

        # 設定全域變數給工具函數使用（通過回調函數的方式）
        import game.utils as utils

        utils._game_state = self  # 傳遞整個遊戲狀態對象

        # 更新爆炸效果
        self.explosions = [
            explosion for explosion in self.explosions if explosion.update()
        ]

        # 更新所有磚塊
        now = pygame.time.get_ticks()
        for brick in self.bricks:
            brick.update(now, self.bricks)

        # 檢查是否所有磚塊都被摧毀
        if all(brick.hit for brick in self.bricks):
            self.level += 1
            # 直接生成新磚塊，不顯示過關訊息
            self.bricks = create_new_bricks()

        # 更新所有球
        alive_any = False
        remove_list = []
        for ball in self.balls:
            alive = ball.update(
                self.paddle, self.bricks, WINDOW_WIDTH, WINDOW_HEIGHT, self.balls, self
            )
            if not alive:
                remove_list.append(ball)
            else:
                alive_any = True

        # 移除死亡的球
        for ball in remove_list:
            if ball in self.balls:
                self.balls.remove(ball)

        # 若沒有任何球存活，遊戲結束（原始版本的機制）
        if not alive_any:
            self.game_over = True
            self.state = "GAME_OVER"

        # 更新碎片
        self.shards = [shard for shard in self.shards if shard.update(WINDOW_HEIGHT)]

        # 更新彩蛋並檢查是否被撿取
        remaining_eggs = []
        for egg in self.eggs:
            alive = egg.update(WINDOW_HEIGHT)
            if not alive:
                continue

            if egg.check_paddle_collision(self.paddle):
                self.score += SCORE_CONFIG["EGG_COLLECTED"]
                continue
            remaining_eggs.append(egg)
        self.eggs = remaining_eggs

    def draw(self, surface):
        """繪製遊戲畫面"""
        # 清空背景
        surface.fill(COLORS["BLACK"])

        if not self.game_over:
            # 繪製所有磚塊
            for brick in self.bricks:
                brick.draw(surface)

            # 繪製玩家底板
            self.paddle.draw(surface)

            # 繪製所有球
            for ball in self.balls:
                ball.draw(surface)

            # 繪製碎片
            for shard in self.shards:
                shard.draw(surface)

            # 繪製彩蛋
            for egg in self.eggs:
                egg.draw(surface)

            # 繪製爆炸效果
            for explosion in self.explosions:
                explosion.draw(surface)

            # 顯示發射提示（與 main.py 一致）
            any_stuck = any(ball.stuck for ball in self.balls)
            if any_stuck:
                text = self.font.render(
                    "Press UP to launch ball", True, COLORS["WHITE"]
                )
                text_rect = text.get_rect(
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
                )
                surface.blit(text, text_rect)
        else:
            # 遊戲結束畫面（與 main.py 一致）
            text = self.font_large.render("GAME OVER", True, COLORS["RED"])
            text_rect = text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)
            )
            surface.blit(text, text_rect)

            # 顯示最終得分
            score_text = self.font.render(
                f"Final Score: {self.score}", True, COLORS["WHITE"]
            )
            score_rect = score_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
            )
            surface.blit(score_text, score_rect)

            restart_text = self.font.render("Press R to restart", True, COLORS["WHITE"])
            restart_rect = restart_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
            )
            surface.blit(restart_text, restart_rect)
