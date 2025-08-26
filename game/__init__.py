# -*- coding: utf-8 -*-
"""
敲磚塊遊戲核心模組

包含遊戲的所有核心功能，包括遊戲物件、特效系統、遊戲邏輯和工具函數。
"""

from .objects import Brick, Paddle, Ball
from .effects import Explosion, Shard, Egg
from .utils import explode_tnt, spawn_shards, spawn_eggs_from_bricks

__version__ = "2.1.0"
__author__ = "遊戲開發者"

__all__ = [
    "Brick",
    "Paddle",
    "Ball",
    "Explosion",
    "Shard",
    "Egg",
    "explode_tnt",
    "spawn_shards",
    "spawn_eggs_from_bricks",
]
