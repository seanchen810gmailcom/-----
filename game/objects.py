# -*- coding: utf-8 -*-
"""
遊戲物件類別模組

包含敲磚塊遊戲中的所有主要物件類別：磚塊、底板、球。
"""

import pygame
import math
import random
from collections import deque
from config import (
    BRICK_CONFIG,
    PADDLE_CONFIG,
    BALL_CONFIG,
    TNT_CONFIG,
    BLINKING_CONFIG,
    COLORS,
    PHYSICS_CONFIG,
)


class Brick:
    """代表一個磚塊的類別。

    建構子參數：x, y, width, height, color, is_tnt
    屬性：
      - hit: 是否已被擊中（被擊中後可設為 True 以避免繪製）
      - is_tnt: 是否為TNT磚塊
      - is_blinking: 是否為會閃爍的特殊磚塊
    """

    def __init__(self, x, y, width=None, height=None, color=None, is_tnt=False):
        # 磚塊左上角座標
        self.x = x
        self.y = y
        # 磚塊大小（使用設定檔的預設值）
        self.width = width or BRICK_CONFIG["WIDTH"]
        self.height = height or BRICK_CONFIG["HEIGHT"]
        # 顏色為 (R, G, B)
        self.color = color or COLORS["BRICK_TOMATO"]
        # 保存原始顏色（用於重置）
        self.base_color = self.color
        # 被擊中狀態
        self.hit = False
        # 是否為TNT磚塊
        self.is_tnt = is_tnt

        # TNT 觸發（priming）相關狀態
        self.tnt_primed = False
        self.tnt_primed_start = 0
        self.tnt_primed_cycles = 0
        self.tnt_blink_duration = TNT_CONFIG["BLINK_DURATION"]
        self.tnt_blink_repeats = TNT_CONFIG["BLINK_REPEATS"]

        # 是否為會閃爍（特殊）磚塊
        self.is_blinking = False
        self.blink_period = BLINKING_CONFIG["PERIOD"]
        self.blink_offset = random.randint(0, 1000)

        # 下落相關屬性
        self.falling = False
        self.target_y = y
        self.fall_speed = PHYSICS_CONFIG["FALL_SPEED"]

    def draw(self, surface):
        """在傳入的 surface 上繪製磚塊（若尚未被擊中）。"""
        if not self.hit:
            draw_color = self.color

            # 如果是會閃爍的磚塊，計算漸變色
            if self.is_blinking:
                palette = COLORS["BLINK_PALETTE"]
                t = (pygame.time.get_ticks() + self.blink_offset) % self.blink_period
                factor = (math.sin(2 * math.pi * (t / self.blink_period)) * 0.5) + 0.5

                # 將 factor 映射到 palette 的多段區間並做線性內插
                segs = len(palette) - 1
                scaled = factor * segs
                idx = int(scaled)
                frac = scaled - idx
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
                t = pygame.time.get_ticks() - self.tnt_primed_start
                period = self.tnt_blink_duration * 2
                phase = (t % period) < self.tnt_blink_duration
                draw_color = COLORS["RED"] if phase else COLORS["WHITE"]

            pygame.draw.rect(
                surface,
                draw_color,
                pygame.Rect(self.x, self.y, self.width, self.height),
            )

            # 如果是TNT磚塊，在上面繪製 "TNT" 文字
            if self.is_tnt:
                from config import FONT_CONFIG

                font = pygame.font.Font(None, FONT_CONFIG["TNT_TEXT_SIZE"])
                text = font.render("TNT", True, COLORS["WHITE"])
                text_rect = text.get_rect(
                    center=(self.x + self.width // 2, self.y + self.height // 2)
                )
                surface.blit(text, text_rect)

    def start_priming(self):
        """當球打到 TNT 時呼叫，開始紅白閃爍倒數。"""
        if not self.is_tnt:
            return
        if self.tnt_primed or self.hit:
            return
        self.tnt_primed = True
        self.tnt_primed_start = pygame.time.get_ticks()
        self.tnt_primed_cycles = 0

    def update(self, now, all_bricks):
        """每幀更新磚塊的狀態：用於處理 TNT 的閃爍與爆炸觸發，以及下落動畫。"""
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

            if cycles_completed >= self.tnt_blink_repeats:
                # 匯入並呼叫爆炸處理
                from .utils import explode_tnt

                explode_tnt(self, all_bricks)
                self.tnt_primed = False
            else:
                self.tnt_primed_cycles = cycles_completed


class Paddle:
    """代表玩家控制的底板。"""

    def __init__(self, x, y, width=None, height=None, color=None, speed=None):
        # 底板左上角座標
        self.x = x
        self.y = y
        # 底板大小（使用設定檔的預設值）
        self.width = width or PADDLE_CONFIG["WIDTH"]
        self.height = height or PADDLE_CONFIG["HEIGHT"]
        # 顏色
        self.color = color or PADDLE_CONFIG["COLOR"]
        # 移動速度
        self.speed = speed or PADDLE_CONFIG["SPEED"]

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


class Ball:
    """代表遊戲中的球。"""

    def __init__(self, x, y, radius=None, color=None, speed=None):
        # 球的中心座標
        self.x = x
        self.y = y
        # 球的半徑（使用設定檔的預設值）
        self.radius = radius or BALL_CONFIG["RADIUS"]
        # 顏色
        self.color = color or BALL_CONFIG["COLOR"]
        # 移動速度
        self.speed = speed or BALL_CONFIG["SPEED"]
        # 速度分量
        self.vx = 0
        self.vy = 0
        # 是否黏在底板上
        self.stuck = True

        # 勝利繞圈的參數
        self.spinning = False
        self.spin_center_x = 0
        self.spin_center_y = 0
        self.spin_radius = 0
        self.spin_angle = 0.0
        self.spin_angular_speed = 0.15

    def update(self, paddle, bricks, screen_width, screen_height, balls_list=None):
        """更新球的位置並處理碰撞。"""
        if self.stuck:
            # 球黏在底板上，跟隨底板移動
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - self.radius
            return True

        # 更新球的位置
        self.x += self.vx
        self.y += self.vy

        # 檢查與邊界的碰撞
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            self.vx = -self.vx
            if self.x - self.radius <= 0:
                self.x = self.radius
            else:
                self.x = screen_width - self.radius
            self.normalize_velocity()

        # 檢查與上邊界的碰撞
        if self.y - self.radius <= 0:
            self.vy = -self.vy
            self.y = self.radius
            self.normalize_velocity()

        # 檢查與下邊界的碰撞（遊戲結束）
        if self.y + self.radius >= screen_height:
            return False

        # 檢查與底板的碰撞
        if (
            self.y + self.radius >= paddle.y
            and self.y - self.radius <= paddle.y + paddle.height
            and self.x >= paddle.x
            and self.x <= paddle.x + paddle.width
        ):

            # 計算球撞到底板的相對位置
            hit_pos = (self.x - paddle.x) / paddle.width
            max_angle = math.radians(PHYSICS_CONFIG["BOUNCE_ANGLE_MAX"])
            angle = (hit_pos - 0.5) * 2 * max_angle

            self.vx = self.speed * math.sin(angle)
            self.vy = -self.speed * math.cos(angle)
            self.y = paddle.y - self.radius

        # 檢查與磚塊的碰撞
        for brick in bricks:
            if not brick.hit and self.check_brick_collision(brick):
                if brick.is_tnt:
                    brick.start_priming()
                else:
                    brick.hit = True
                    # 產生碎片效果
                    try:
                        from .utils import spawn_shards

                        spawn_shards(brick, count=8)
                    except Exception:
                        pass

                    # 增加得分（需要在主程式中處理）
                    from config import SCORE_CONFIG

                    global score
                    if "score" in globals():
                        score += SCORE_CONFIG["BRICK_HIT"]

                # 如果撞到閃爍磚塊，產生額外的球
                if brick.is_blinking and balls_list is not None:
                    for _ in range(BLINKING_CONFIG["EXTRA_BALLS"]):
                        new_ball = Ball(
                            self.x, self.y, self.radius, self.color, self.speed
                        )
                        new_ball.stuck = False
                        angle = random.uniform(-math.pi, math.pi)
                        new_ball.vx = math.cos(angle) * new_ball.speed
                        new_ball.vy = math.sin(angle) * new_ball.speed
                        balls_list.append(new_ball)

                # 簡單的反彈邏輯
                if self.x < brick.x or self.x > brick.x + brick.width:
                    self.vx = -self.vx
                if self.y < brick.y or self.y > brick.y + brick.height:
                    self.vy = -self.vy

                # 保持速度大小
                angle = math.atan2(self.vy, self.vx)
                self.vx = math.cos(angle) * self.speed
                self.vy = math.sin(angle) * self.speed
                break

        return True

    def check_brick_collision(self, brick):
        """檢查球是否與磚塊碰撞。"""
        closest_x = max(brick.x, min(self.x, brick.x + brick.width))
        closest_y = max(brick.y, min(self.y, brick.y + brick.height))

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
        """開始繞圈動畫。"""
        self.spinning = True
        self.spin_center_x = center_x
        self.spin_center_y = center_y
        self.spin_radius = radius
        self.spin_angle = math.atan2(self.y - center_y, self.x - center_x)
        self.spin_angular_speed = 0.12

    def update_spin(self):
        """每幀更新繞圈位置。"""
        if not self.spinning:
            return
        self.spin_angle += self.spin_angular_speed
        self.x = self.spin_center_x + math.cos(self.spin_angle) * self.spin_radius
        self.y = self.spin_center_y + math.sin(self.spin_angle) * self.spin_radius

    def draw(self, surface):
        """在傳入的 surface 上繪製球。"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def normalize_velocity(self):
        """將當前速度分量重新正規化。"""
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            self.vx = 0
            self.vy = -self.speed
            return
        self.vx = (self.vx / mag) * self.speed
        self.vy = (self.vy / mag) * self.speed
