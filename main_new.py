"""
敲磚塊遊戲 - 主程式

這是重構後的主程式，使用模組化的架構。
"""

######################載入套件######################
import pygame
import sys
import os

######################導入遊戲模組######################
from config import *
from game.game_logic import GameState

######################物件類別######################


class BreakoutGame:
    """
    敲磚塊遊戲主類別\n
    \n
    負責管理整個遊戲的運行流程，包含：\n
    1. Pygame 初始化與視窗設定\n
    2. 遊戲狀態管理與更新\n
    3. 事件處理與使用者輸入\n
    4. 畫面繪製與 UI 顯示\n
    \n
    屬性:\n
    screen (pygame.Surface): 主遊戲視窗\n
    clock (pygame.time.Clock): 用於控制遊戲 FPS 的時鐘\n
    game_state (GameState): 遊戲狀態管理物件\n
    font (pygame.font.Font): 一般文字字體\n
    large_font (pygame.font.Font): 大標題字體\n
    \n
    使用範例:\n
    game = BreakoutGame()\n
    game.run()  # 開始執行遊戲主迴圈\n
    """

    def __init__(self):
        """
        初始化遊戲系統\n
        \n
        執行步驟：\n
        1. 初始化 Pygame 系統\n
        2. 創建遊戲視窗並設定標題\n
        3. 設定 FPS 控制時鐘\n
        4. 創建遊戲狀態管理物件\n
        5. 載入遊戲所需字體\n
        """
        # 啟動 Pygame 系統，讓我們可以使用圖形和聲音功能
        pygame.init()

        # 創建遊戲視窗，大小根據設定檔決定
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("敲磚塊遊戲 v2.0")

        # 設定時鐘來控制遊戲跑多快，避免電腦太快讓遊戲跑太快
        self.clock = pygame.time.Clock()

        # 創建遊戲狀態物件，用來管理所有遊戲邏輯
        self.game_state = GameState()

        # 載入字體，如果載入失敗就用系統預設字體
        try:
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 72)
        except:
            # 如果找不到字體檔案，就用系統的 arial 字體
            self.font = pygame.font.SysFont("arial", 36)
            self.large_font = pygame.font.SysFont("arial", 72)

    def handle_events(self):
        """
        處理使用者輸入事件\n
        \n
        檢查所有使用者的操作（按鍵、關閉視窗等）\n
        並將這些操作傳給遊戲狀態來處理\n
        \n
        回傳:\n
        bool: True 表示遊戲應該繼續執行，False 表示使用者想要退出\n
        """
        # 檢查所有發生的事件（滑鼠點擊、按鍵等）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 使用者點了視窗右上角的 X 按鈕，想要關閉遊戲
                return False

            # 讓遊戲狀態處理其他事件（按鍵等）
            self.game_state.handle_events(event)

        # 回傳遊戲是否還要繼續執行
        return self.game_state.running

    def update(self):
        """
        更新遊戲狀態\n
        \n
        每一幀都會呼叫這個方法來更新所有遊戲物件的狀態，\n
        包含球的移動、碰撞檢測、磚塊狀態等等\n
        """
        # 讓遊戲狀態物件更新所有遊戲邏輯
        self.game_state.update()

    def draw(self):
        """
        繪製遊戲畫面\n
        \n
        每一幀都會呼叫這個方法來畫出所有遊戲物件，\n
        包含磚塊、球、底板、特效、UI 文字等等\n
        """
        # 把整個螢幕塗成黑色，清除上一幀的內容
        self.screen.fill(COLORS["BLACK"])

        # 讓遊戲狀態繪製所有遊戲物件
        self.game_state.draw(self.screen)

        # 繪製使用者介面（分數等資訊）
        self.draw_ui()

        # 把所有畫好的內容顯示到螢幕上
        pygame.display.flip()

    def draw_ui(self):
        """
        繪製使用者介面元素\n
        \n
        顯示遊戲資訊如分數、生命值等等\n
        目前只顯示分數在右上角，與原版 main.py 保持一致\n
        """
        # 產生分數文字，白色字體
        score_text = self.font.render(
            f"Score: {self.game_state.score}", True, COLORS["WHITE"]
        )
        # 計算要放在右上角的位置
        score_rect = score_text.get_rect()
        score_rect.topright = (WINDOW_WIDTH - 10, 10)
        # 把分數文字畫到螢幕上
        self.screen.blit(score_text, score_rect)

    def run(self):
        """
        執行遊戲主迴圈\n
        \n
        這是遊戲的心臟，會一直重複執行直到遊戲結束：\n
        1. 處理使用者輸入\n
        2. 更新遊戲狀態\n
        3. 繪製畫面\n
        4. 控制 FPS 避免跑太快\n
        \n
        異常處理:\n
        - KeyboardInterrupt: 使用者按 Ctrl+C 中斷\n
        - Exception: 其他執行錯誤\n
        - 無論如何都會執行清理程序\n
        """
        # 印出遊戲啟動訊息和操作說明
        print("🎮 敲磚塊遊戲 v2.0 啟動！")
        print("=" * 40)
        print("控制說明:")
        print("  ← → 或 A D: 移動球拍")
        print("  SPACE: 暫停/繼續")
        print("  R: 重新開始")
        print("  ESC: 退出遊戲")
        print("=" * 40)

        # 遊戲是否還在執行的旗標
        running = True

        try:
            # 遊戲主迴圈，會一直重複執行直到遊戲結束
            while running:
                # 處理使用者的輸入（按鍵、滑鼠等）
                running = self.handle_events()

                # 更新所有遊戲物件的狀態
                self.update()

                # 把所有東西畫到螢幕上
                self.draw()

                # 控制遊戲速度，讓遊戲以固定 FPS 執行
                self.clock.tick(FPS)

        except KeyboardInterrupt:
            # 使用者按 Ctrl+C 想要強制結束遊戲
            print("\n👋 遊戲被使用者中斷")
        except Exception as e:
            # 遊戲執行時發生其他錯誤
            print(f"❌ 遊戲執行時發生錯誤: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # 無論遊戲怎麼結束，都要清理資源
            self.cleanup()

    def cleanup(self):
        """
        清理遊戲資源\n
        \n
        遊戲結束時執行，釋放所有佔用的系統資源，\n
        確保程式乾淨地結束不會留下垃圾\n
        """
        print("🧹 清理遊戲資源...")
        # 關閉 Pygame 系統，釋放所有資源
        pygame.quit()
        print("👋 感謝遊玩！")


######################定義函式區######################


def main():
    """
    程式主函數\n
    \n
    負責檢查系統環境、載入必要模組、創建遊戲物件並啟動遊戲。\n
    包含完整的錯誤處理，確保使用者能得到清楚的錯誤訊息。\n
    \n
    執行步驟:\n
    1. 檢查 Pygame 是否正確安裝和初始化\n
    2. 檢查遊戲模組是否可以正常載入\n
    3. 創建遊戲物件並開始執行\n
    4. 處理可能發生的各種錯誤\n
    \n
    回傳:\n
    int: 程式退出碼，0 表示成功，1 表示失敗\n
    """
    # 檢查 Pygame 是否正確安裝，這是遊戲運行的基礎
    try:
        pygame.init()
        print("✅ Pygame 已正確載入")
    except Exception as e:
        print(f"❌ Pygame 載入失敗: {e}")
        print("請確認已安裝 Pygame: pip install pygame")
        return 1

    # 檢查遊戲模組是否存在，確保檔案結構完整
    try:
        from game.game_logic import GameState

        print("✅ 遊戲模組已正確載入")
    except ImportError as e:
        print(f"❌ 無法載入遊戲模組: {e}")
        print("請確認遊戲檔案結構完整")
        return 1

    # 創建並運行遊戲，這裡是真正開始玩遊戲的地方
    try:
        game = BreakoutGame()
        game.run()
        return 0
    except Exception as e:
        print(f"❌ 遊戲啟動失敗: {e}")
        return 1


######################主程式######################

# 直接呼叫主函數，不使用 if __name__ == "__main__" 慣例
exit_code = main()
sys.exit(exit_code)
