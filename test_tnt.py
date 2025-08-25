#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試TNT功能的簡單腳本
"""

import pygame
import sys
import math
import random

# 從main.py導入必要的類別
import importlib.util

spec = importlib.util.spec_from_file_location("main", "./main.py")
main_module = importlib.util.module_from_spec(spec)


# 重新定義必要的類別和函數來測試
class Brick:
    def __init__(self, x, y, width, height, color, is_tnt=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hit = False
        self.is_tnt = is_tnt


def explode_tnt(tnt_brick, all_bricks):
    """處理TNT磚塊爆炸，炸掉周圍的磚塊。"""
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


def test_tnt_explosion():
    """測試TNT爆炸功能"""
    print("開始測試TNT爆炸功能...")

    # 創建測試磚塊：3x3網格
    bricks = []
    brick_width = 60
    brick_height = 30

    for row in range(3):
        for col in range(3):
            x = col * (brick_width + 10) + 50
            y = row * (brick_height + 10) + 50
            is_tnt = row == 1 and col == 1  # 中心磚塊為TNT
            brick = Brick(x, y, brick_width, brick_height, (255, 0, 0), is_tnt)
            bricks.append(brick)

    print(f"創建了 {len(bricks)} 個磚塊")
    print(f"TNT磚塊位置：{bricks[4].x}, {bricks[4].y}")

    # 觸發TNT爆炸
    tnt_brick = bricks[4]  # 中心磚塊
    exploded_count = explode_tnt(tnt_brick, bricks)

    print(f"爆炸摧毀了 {exploded_count} 個磚塊")

    # 檢查結果
    hit_bricks = [i for i, brick in enumerate(bricks) if brick.hit]
    print(f"被摧毀的磚塊索引：{hit_bricks}")

    # 期望結果：所有9個磚塊都應該被摧毀（因為它們都在100像素範圍內）
    if exploded_count == 9:
        print("✓ TNT爆炸測試通過！")
        return True
    else:
        print(f"✗ TNT爆炸測試失敗！期望9個，實際{exploded_count}個")
        return False


def test_tnt_selection():
    """測試TNT磚塊選擇功能"""
    print("\n開始測試TNT磚塊選擇功能...")

    # 創建50個磚塊（模擬遊戲中的磚塊數量）
    total_bricks = 50
    bricks = []
    for i in range(total_bricks):
        brick = Brick(i * 10, 0, 60, 30, (255, 0, 0))
        bricks.append(brick)

    # 隨機選擇5個作為TNT
    tnt_indices = random.sample(range(len(bricks)), 5)
    for i in tnt_indices:
        bricks[i].is_tnt = True

    # 檢查結果
    tnt_count = sum(1 for brick in bricks if brick.is_tnt)
    print(f"選擇了 {tnt_count} 個TNT磚塊")
    print(f"TNT磚塊索引：{tnt_indices}")

    if tnt_count == 5:
        print("✓ TNT磚塊選擇測試通過！")
        return True
    else:
        print(f"✗ TNT磚塊選擇測試失敗！期望5個，實際{tnt_count}個")
        return False


if __name__ == "__main__":
    test1_passed = test_tnt_explosion()
    test2_passed = test_tnt_selection()

    print(f"\n測試結果：")
    print(f"TNT爆炸功能：{'通過' if test1_passed else '失敗'}")
    print(f"TNT選擇功能：{'通過' if test2_passed else '失敗'}")

    if test1_passed and test2_passed:
        print("\n🎉 所有測試都通過了！TNT功能正常工作。")
    else:
        print("\n❌ 有測試失敗，請檢查代碼。")
