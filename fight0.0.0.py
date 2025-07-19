import random
import time
import pyautogui


class Game:
    def __init__(self):
        self.our_action = "pass"
        self.ai_action = "pass"
        self.our_bullets = 0
        self.ai_bullets = 0
        self.choose = ["stockpile", "defense", "fight", "break_defense"]
        self.final_result = "unknown"

        # 配置
        self.can_break_defense = 10
        self.can_fight = 1
        self.can_stockpile = 1

        # 控制键位
        self.key_stockpile = "0"
        self.key_defense = "1"
        self.key_fight = "2"
        self.key_break_defense = "3"

    def ai_choose(self):
        if self.ai_bullets < self.can_fight:
            return random.choice(self.choose[:2])  # stockpile or defense
        elif self.ai_bullets < self.can_break_defense:
            return random.choice(self.choose[:3])  # stockpile, defense, or fight
        else:
            return random.choice(self.choose)  # all options

    def determine_winner(self):
        if (self.our_action == "fight" or self.our_action == "break_defense") and self.ai_action == "stockpile":
            return "Our_win"
        elif self.our_action == "break_defense" and self.ai_action == "defense":
            return "Our_win"
        elif (self.ai_action == "fight" or self.ai_action == "break_defense") and self.our_action == "stockpile":
            return "AI_win"
        elif self.ai_action == "break_defense" and self.our_action == "defense":
            return "AI_win"
        else:
            return "Continue"

    def play(self):
        while True:
            print("你要干嘛\n1.开始游戏\n2.退出\n3.设置")
            choice = input()
            if choice == "1":
                self.start_game()
            elif choice == "2":
                print("已退出")
                break
            elif choice == "3":
                self.settings()
            else:
                keyboard.press("shift+c")
                keyboard.release("shift+c")

    def start_game(self):
        self.our_bullets = 0
        self.ai_bullets = 0
