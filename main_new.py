"""
敲磚塊遊戲 - 主程式

這是重構後的主程式，使用模組化的架構。
"""

import pygame
import sys
import os

# 導入遊戲模組
from config import *
from game.game_logic import GameState


class BreakoutGame:
    """敲磚塊遊戲主類別"""

    def __init__(self):
        """初始化遊戲"""
        # 初始化 Pygame
        pygame.init()

        # 創建遊戲視窗
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("敲磚塊遊戲 v2.0")

        # 設定時鐘
        self.clock = pygame.time.Clock()

        # 創建遊戲狀態
        self.game_state = GameState()

        # 載入字體
        try:
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 72)
        except:
            self.font = pygame.font.SysFont("arial", 36)
            self.large_font = pygame.font.SysFont("arial", 72)

    def handle_events(self):
        """處理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # 讓遊戲狀態處理事件
            self.game_state.handle_events(event)

        return self.game_state.running

    def update(self):
        """更新遊戲狀態"""
        self.game_state.update()

    def draw(self):
        """繪製遊戲畫面"""
        # 清除螢幕
        self.screen.fill(COLORS["BLACK"])

        # 繪製遊戲狀態
        self.game_state.draw(self.screen)

        # 繪製 UI
        self.draw_ui()

        # 更新顯示
        pygame.display.flip()

    def draw_ui(self):
        """繪製使用者介面"""
        # 繪製分數
        score_text = self.font.render(
            f"分數: {self.game_state.score}", True, COLORS["WHITE"]
        )
        self.screen.blit(score_text, (10, 10))

        # 繪製生命值
        lives_text = self.font.render(
            f"生命: {self.game_state.lives}", True, COLORS["WHITE"]
        )
        self.screen.blit(lives_text, (10, 50))

        # 繪製等級
        level_text = self.font.render(
            f"等級: {self.game_state.level}", True, COLORS["WHITE"]
        )
        self.screen.blit(level_text, (10, 90))

        # 繪製 TNT 數量
        tnt_text = self.font.render(
            f"TNT: {self.game_state.tnt_count}", True, COLORS["YELLOW"]
        )
        self.screen.blit(tnt_text, (WINDOW_WIDTH - 100, 10))

        # 根據遊戲狀態繪製特殊訊息
        if self.game_state.state == "PAUSED":
            pause_text = self.large_font.render("遊戲暫停", True, COLORS["WHITE"])
            text_rect = pause_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            self.screen.blit(pause_text, text_rect)

            instruction_text = self.font.render("按 SPACE 繼續", True, COLORS["WHITE"])
            inst_rect = instruction_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
            )
            self.screen.blit(instruction_text, inst_rect)

        elif self.game_state.state == "GAME_OVER":
            game_over_text = self.large_font.render("遊戲結束", True, COLORS["RED"])
            text_rect = game_over_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            self.screen.blit(game_over_text, text_rect)

            final_score_text = self.font.render(
                f"最終分數: {self.game_state.score}", True, COLORS["WHITE"]
            )
            score_rect = final_score_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
            )
            self.screen.blit(final_score_text, score_rect)

            restart_text = self.font.render("按 R 重新開始", True, COLORS["WHITE"])
            restart_rect = restart_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90)
            )
            self.screen.blit(restart_text, restart_rect)

        elif self.game_state.state == "LEVEL_COMPLETE":
            level_complete_text = self.large_font.render(
                "過關！", True, COLORS["GREEN"]
            )
            text_rect = level_complete_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            self.screen.blit(level_complete_text, text_rect)

            next_level_text = self.font.render(
                "準備進入下一關...", True, COLORS["WHITE"]
            )
            next_rect = next_level_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
            )
            self.screen.blit(next_level_text, next_rect)

    def run(self):
        """運行遊戲主迴圈"""
        print("🎮 敲磚塊遊戲 v2.0 啟動！")
        print("=" * 40)
        print("控制說明:")
        print("  ← → 或 A D: 移動球拍")
        print("  SPACE: 暫停/繼續")
        print("  R: 重新開始")
        print("  ESC: 退出遊戲")
        print("  滑鼠左鍵: 放置 TNT")
        print("=" * 40)

        running = True

        try:
            while running:
                # 處理事件
                running = self.handle_events()

                # 更新遊戲
                self.update()

                # 繪製畫面
                self.draw()

                # 控制 FPS
                self.clock.tick(FPS)

        except KeyboardInterrupt:
            print("\n👋 遊戲被使用者中斷")
        except Exception as e:
            print(f"❌ 遊戲執行時發生錯誤: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """清理資源"""
        print("🧹 清理遊戲資源...")
        pygame.quit()
        print("👋 感謝遊玩！")


def main():
    """主函數"""
    # 檢查 Pygame 是否正確安裝
    try:
        pygame.init()
        print("✅ Pygame 已正確載入")
    except Exception as e:
        print(f"❌ Pygame 載入失敗: {e}")
        print("請確認已安裝 Pygame: pip install pygame")
        return 1

    # 檢查模組是否存在
    try:
        from game.game_logic import GameState

        print("✅ 遊戲模組已正確載入")
    except ImportError as e:
        print(f"❌ 無法載入遊戲模組: {e}")
        print("請確認遊戲檔案結構完整")
        return 1

    # 創建並運行遊戲
    try:
        game = BreakoutGame()
        game.run()
        return 0
    except Exception as e:
        print(f"❌ 遊戲啟動失敗: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
