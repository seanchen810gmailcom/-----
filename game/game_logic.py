# -*- coding: utf-8 -*-
"""
遊戲邏輯模組

包含遊戲狀態管理、得分系統、遊戲流程控制等核心邏輯。
"""

import pygame
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PADDLE_CONFIG,
    BALL_CONFIG,
    FONT_CONFIG,
    COLORS,
    SCORE_CONFIG,
)
from .objects import Paddle, Ball
from .utils import initialize_bricks, create_new_bricks


class GameState:
    """遊戲狀態管理類別"""

    def __init__(self):
        self.score = 0
        self.lives = 3  # 新增生命值
        self.level = 1  # 新增等級
        self.tnt_count = 0  # 新增 TNT 數量
        self.state = (
            "PLAYING"  # 新增遊戲狀態 (PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE)
        )
        self.game_over = False
        self.running = True

        # 初始化字體
        self.font = pygame.font.Font(None, FONT_CONFIG["DEFAULT_SIZE"])
        self.font_large = pygame.font.Font(None, FONT_CONFIG["LARGE_SIZE"])

        # 初始化遊戲物件
        self.reset_game()

    def reset_game(self):
        """重置遊戲狀態"""
        self.game_over = False
        self.state = "PLAYING"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.tnt_count = 0

        # 初始化磚塊
        self.bricks = initialize_bricks()

        # 初始化底板
        paddle_x = (WINDOW_WIDTH - PADDLE_CONFIG["WIDTH"]) // 2
        paddle_y = WINDOW_HEIGHT - PADDLE_CONFIG["MARGIN_BOTTOM"]
        self.paddle = Paddle(paddle_x, paddle_y)

        # 初始化球
        self.balls = []
        main_ball = Ball(
            self.paddle.x + self.paddle.width // 2,
            self.paddle.y - BALL_CONFIG["RADIUS"],
        )
        self.balls.append(main_ball)

        # 特效列表
        self.explosions = []
        self.shards = []
        self.eggs = []

    def handle_events(self, event):
        """處理遊戲事件"""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.USEREVENT + 1:
            # 關卡完成後生成新磚塊
            if self.state == "LEVEL_COMPLETE":
                self.bricks = create_new_bricks()
                self.state = "PLAYING"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 發射所有仍黏在底板上的球
                for ball in self.balls:
                    if ball.stuck:
                        ball.launch()
            elif event.key == pygame.K_r and (
                self.game_over or self.state == "GAME_OVER"
            ):
                # 重新開始遊戲
                self.reset_game()
            elif event.key == pygame.K_SPACE:
                # 暫停/繼續遊戲
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                elif self.state == "PAUSED":
                    self.state = "PLAYING"
            elif event.key == pygame.K_ESCAPE:
                # 退出遊戲
                self.running = False

    def handle_continuous_input(self):
        """處理連續輸入（移動底板）"""
        if not self.game_over and self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.paddle.move_left(WINDOW_WIDTH)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.paddle.move_right(WINDOW_WIDTH)

    def update(self):
        """更新遊戲狀態"""
        # 如果遊戲暫停或結束，不更新遊戲邏輯
        if self.state != "PLAYING" or self.game_over:
            return

        # 處理連續輸入
        self.handle_continuous_input()

        # 讓全域變數可被工具函數使用
        import game.utils as utils

        utils.score = self.score
        utils.explosions = self.explosions
        utils.shards = self.shards
        utils.eggs = self.eggs

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
            self.state = "LEVEL_COMPLETE"
            # 延遲後生成新磚塊
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # 2秒後觸發事件

        # 更新所有球
        alive_any = False
        remove_list = []
        for ball in self.balls:
            alive = ball.update(
                self.paddle, self.bricks, WINDOW_WIDTH, WINDOW_HEIGHT, self.balls
            )
            if not alive:
                remove_list.append(ball)
            else:
                alive_any = True

        # 移除死亡的球
        for ball in remove_list:
            if ball in self.balls:
                self.balls.remove(ball)

        # 若沒有任何球存活，失去一條生命
        if not alive_any:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.state = "GAME_OVER"
            else:
                # 重新生成球
                main_ball = Ball(
                    self.paddle.x + self.paddle.width // 2,
                    self.paddle.y - BALL_CONFIG["RADIUS"],
                )
                self.balls.append(main_ball)

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

        # 更新得分（從工具函數同步回來）
        if hasattr(utils, "score"):
            self.score = utils.score

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

            # 在右上角顯示得分
            score_text = self.font.render(f"Score: {self.score}", True, COLORS["WHITE"])
            score_rect = score_text.get_rect()
            score_rect.topright = (WINDOW_WIDTH - 10, 10)
            surface.blit(score_text, score_rect)

            # 顯示發射提示
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
            # 遊戲結束畫面
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
