# -*- coding: utf-8 -*-
"""
遊戲工具函數模組

包含 TNT 爆炸處理、碎片生成、彩蛋生成等輔助函數。
"""

######################載入套件######################
import math
import random
from collections import deque

######################導入設定######################
from config import TNT_CONFIG, EFFECTS_CONFIG, SCORE_CONFIG


######################全域變數######################
# 用於與主程式通信的全域變數
_game_state = None


######################定義函式區######################


def explode_tnt(tnt_brick, all_bricks):
    """
    處理TNT磚塊爆炸，炸掉周圍的磚塊\n
    \n
    使用廣度優先搜索（BFS）算法處理連鎖爆炸，\n
    避免遞迴深度過深的問題。當 TNT 爆炸時，\n
    會炸掉範圍內的所有磚塊，如果範圍內有其他 TNT\n
    也會觸發連鎖爆炸。\n
    \n
    參數:\n
    tnt_brick (Brick): 被擊中的 TNT 磚塊\n
    all_bricks (list): 所有磚塊的列表\n
    \n
    回傳:\n
    int: 被炸掉的磚塊數量（包含 TNT 本身）\n
    \n
    算法說明:\n
    1. 使用佇列處理連鎖爆炸，避免遞迴\n
    2. 每個 TNT 爆炸都會產生視覺效果\n
    3. 計算距離時使用歐幾里得距離\n
    4. 被炸到的 TNT 會加入佇列等待處理\n
    """
    global _game_state

    # 使用佇列處理連鎖爆炸（BFS）
    exploded_count = 0
    explosion_radius = TNT_CONFIG["EXPLOSION_RADIUS"]

    queue = deque()

    # 添加爆炸效果
    explosion_x = tnt_brick.x + tnt_brick.width // 2
    explosion_y = tnt_brick.y + tnt_brick.height // 2

    # 創建爆炸效果
    try:
        from .effects import Explosion

        if _game_state:
            _game_state.explosions.append(Explosion(explosion_x, explosion_y))
    except Exception:
        pass

    # 若傳入的 tnt_brick 尚未被標記為 hit，則先標記並計數
    if not tnt_brick.hit:
        tnt_brick.hit = True
        exploded_count += 1
        if _game_state:
            _game_state.score += SCORE_CONFIG["TNT_EXPLOSION"]

    # 將這顆 TNT 加入處理佇列以檢查其範圍內的磚塊
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
                if _game_state:
                    try:
                        spawn_shards(brick, count=10)
                    except Exception:
                        pass
                exploded_count += 1
                if _game_state:
                    _game_state.score += SCORE_CONFIG["TNT_DESTROYED"]

                # 如果被炸到的也是TNT，加入佇列以觸發連鎖，並添加爆炸效果
                if brick.is_tnt:
                    queue.append(brick)
                    explosion_x = brick.x + brick.width // 2
                    explosion_y = brick.y + brick.height // 2
                    try:
                        from .effects import Explosion

                        if _game_state:
                            _game_state.explosions.append(
                                Explosion(explosion_x, explosion_y)
                            )
                    except Exception:
                        pass

    return exploded_count


def spawn_shards(brick, count=None):
    """從磚塊位置產生碎片"""
    global _game_state

    if count is None:
        count = EFFECTS_CONFIG["SHARD_COUNT"]

    try:
        from .effects import Shard

        if _game_state:
            for _ in range(count):
                sx = random.uniform(brick.x, brick.x + brick.width)
                sy = random.uniform(brick.y, brick.y + brick.height)
                # 使用磚塊原色作為碎片顏色
                color = getattr(brick, "base_color", brick.color)
                _game_state.shards.append(Shard(sx, sy, color))
    except Exception:
        pass


def spawn_eggs_from_bricks(bricks_list, num_eggs=5):
    """根據剛清完的磚塊清單，產生一些彩蛋。"""
    global _game_state

    try:
        from .effects import Egg

        if not _game_state:
            return

        available = [b for b in bricks_list]
        if not available:
            return

        # 優先使用已被打掉的磚的位置
        dead_bricks = [b for b in bricks_list if b.hit]
        if dead_bricks:
            sample_src = dead_bricks
        else:
            sample_src = bricks_list

        for i in range(num_eggs):
            src = random.choice(sample_src)
            cx = src.x + src.width / 2
            cy = src.y + src.height / 2
            # 把彩蛋稍微往上偏移
            ex = cx + random.uniform(-20, 20)
            ey = cy + random.uniform(-10, 10)
            # 若該座標在畫面外，調整到畫面上方
            if ey < 0:
                ey = random.uniform(20, 80)
                ex = random.uniform(60, 800 - 60)  # 假設螢幕寬度800
            _game_state.eggs.append(Egg(ex, ey))
    except Exception:
        pass


def create_new_bricks():
    """創建新的磚塊陣列，從視窗上方開始滑下"""
    from .objects import Brick
    from config import BRICK_CONFIG, WINDOW_WIDTH, ROW_COLORS

    new_bricks = []

    # 首先創建所有磚塊（從視窗上方開始，y座標為負數讓它們滑下來）
    for row in range(BRICK_CONFIG["ROWS"]):
        for col in range(BRICK_CONFIG["COLS"]):
            x = BRICK_CONFIG["MARGIN_LEFT"] + col * (
                BRICK_CONFIG["WIDTH"] + BRICK_CONFIG["SPACING_X"]
            )
            y = -BRICK_CONFIG["HEIGHT"] * (BRICK_CONFIG["ROWS"] - row) + row * (
                BRICK_CONFIG["HEIGHT"] + BRICK_CONFIG["SPACING_Y"]
            )
            color = ROW_COLORS[row % len(ROW_COLORS)]
            brick = Brick(x, y, BRICK_CONFIG["WIDTH"], BRICK_CONFIG["HEIGHT"], color)
            brick.target_y = BRICK_CONFIG["MARGIN_TOP"] + row * (
                BRICK_CONFIG["HEIGHT"] + BRICK_CONFIG["SPACING_Y"]
            )
            brick.falling = True
            new_bricks.append(brick)

    # 隨機選擇磚塊設為TNT
    tnt_indices = random.sample(range(len(new_bricks)), BRICK_CONFIG["TNT_COUNT"])
    for i in tnt_indices:
        new_bricks[i].is_tnt = True
        new_bricks[i].color = (139, 69, 19)  # 棕色

    # 選擇磚塊設為會閃爍的特殊磚塊
    non_tnt_indices = [i for i in range(len(new_bricks)) if not new_bricks[i].is_tnt]
    if len(non_tnt_indices) >= BRICK_CONFIG["BLINKING_COUNT"]:
        blinking_indices = random.sample(
            non_tnt_indices, BRICK_CONFIG["BLINKING_COUNT"]
        )
    else:
        blinking_indices = non_tnt_indices
    for i in blinking_indices:
        new_bricks[i].is_blinking = True
        new_bricks[i].color = new_bricks[i].base_color

    return new_bricks


def initialize_bricks():
    """初始化磚塊陣列（遊戲開始時）"""
    from .objects import Brick
    from config import BRICK_CONFIG, ROW_COLORS

    bricks = []

    # 創建所有磚塊
    for row in range(BRICK_CONFIG["ROWS"]):
        for col in range(BRICK_CONFIG["COLS"]):
            x = BRICK_CONFIG["MARGIN_LEFT"] + col * (
                BRICK_CONFIG["WIDTH"] + BRICK_CONFIG["SPACING_X"]
            )
            y = BRICK_CONFIG["MARGIN_TOP"] + row * (
                BRICK_CONFIG["HEIGHT"] + BRICK_CONFIG["SPACING_Y"]
            )
            color = ROW_COLORS[row % len(ROW_COLORS)]
            brick = Brick(x, y, BRICK_CONFIG["WIDTH"], BRICK_CONFIG["HEIGHT"], color)
            brick.target_y = y
            brick.falling = False
            bricks.append(brick)

    # 隨機選擇磚塊設為TNT
    tnt_indices = random.sample(range(len(bricks)), BRICK_CONFIG["TNT_COUNT"])
    for i in tnt_indices:
        bricks[i].is_tnt = True
        bricks[i].color = (139, 69, 19)  # 棕色

    # 選擇磚塊設為會閃爍的特殊磚塊
    non_tnt_indices = [i for i in range(len(bricks)) if not bricks[i].is_tnt]
    if len(non_tnt_indices) >= BRICK_CONFIG["BLINKING_COUNT"]:
        blinking_indices = random.sample(
            non_tnt_indices, BRICK_CONFIG["BLINKING_COUNT"]
        )
    else:
        blinking_indices = non_tnt_indices
    for i in blinking_indices:
        bricks[i].is_blinking = True
        bricks[i].color = bricks[i].base_color

    return bricks
