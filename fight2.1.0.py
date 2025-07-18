'''
版本：2.1.0

更新内容：
1.整理了部分代码

'''
import random
import time
import os

#这个你要导入
try:
    import keyboard
except:
    what = input("你没有导入 “keyboard”，程序可能会报错")

#清屏快捷键
def clear():
    keyboard.press("shift+c")
    keyboard.release("c+shift")
    time.sleep(0.1)

#登录状态
login_state = False

#对局数量
game_nmu = 0
#对局缓存
game_round = []
#对局永存
game_round_retain = {}

#我方行为
Our = "pass"
#AI行为
AI = "pass"
#我方子弹数量
Our_power = 0
#AI子弹数量
AI_power = 0
#选择
choose = ["stockpile","defense","fight","Break_Defense"]
#输赢
finale = "unkonw"

angry = 0

#几发子弹可以破防
Can_Break_Defense = 10
#一枪需要几发子弹
Can_fight = 1
#一次攒几发子弹
Can_stockpile = 1

#攒子弹的键位
key_stockpile = "0"
#防御的键位
key_defense = "1"
#攻击的键位
key_fight = "2"
#破防的键位
key_Break_Defense = "3"

#关于存放用户信息的文件夹
def user():
    if os.path.exists("user"):
        pass
    else:
        os.mkdir("user")

#纯随机的AI
def AI_choose(AI_power):
    #如果子弹不够，就选择 "stockpile","defense"其中一个
    if int(AI_power) < int(Can_fight):
        return (choose[random.randint(0,1)])
    # 如果子弹不超过破防所需，就选择 "stockpile","defense"，"fight"其中一个
    elif int(AI_power) >= int(Can_fight) and int(AI_power) < int(Can_Break_Defense):
        return (choose[random.randint(0, 2)])
    # 如何子弹超过等于破防所需，就选择 "stockpile","defense"，"fight"，"Break_Defense"其中一个
    else:
        return (choose[random.randint(0, 3)])


# 判断是否结束
def Win_Lose(Our,AI):
    # 我方攻击，AI攒子弹 我方获胜
    if (Our == "fight" or Our == "Break_Defense") and AI == "stockpile":
        return "Our_win"
    # 我方十发子弹并攻击，敌方防御 破防敌方，我方获胜
    elif Our == "Break_Defense" and (not AI == "Break_Defense"):
        return "Our_win"
    # 敌方攻击，我方攒子弹 敌方获胜
    elif (AI == "fight" or AI == "Break_Defense") and Our == "stockpile":
        return "AI_win"
    # 敌方十发子弹并攻击，我方防御 破防我方，敌方获胜
    elif AI == "Break_Defense" and (not Our == "Break_Defense"):
        return "AI_win"
    # 继续
    else:
        return "Continue"

#菜单功能 3.设置
def set():
    print("请输入几发才可开枪（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        Can_fight = Can_fight
    else:
        Can_fight = what

    clear()

    print("请输入几发才可破防（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        Can_Break_Defense = Can_Break_Defense
    else:
        Can_Break_Defense = what
    clear()

    print("请输入一次能攒几发子弹（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        Can_stockpile = Can_stockpile
    else:
        Can_stockpile = what
    clear()

    print("请输入攒子弹的键位（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        key_stockpile = key_stockpile
    else:
        key_stockpile = what
    clear()

    print("请输入防御的键位（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        key_defense = key_defense
    else:
        key_defense = what
    clear()

    print("请输入攻击的键位（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        key_fight = key_fight
    else:
        key_fight = what
    clear()

    print("请输入破防的键位（跳过请键入“pass”或直接回车）")
    what = input()
    if what == "pass" or what == "":
        key_Break_Defense = key_Break_Defense
    else:
        key_Break_Defense = what
    clear()

#菜单功能 4.查看对局
def view_match():
    what = input("查看最近对局（输入1）或查看历史对局（输入2）")

    #查看最近对局
    if what == "1":
        clear()
        if game_round == []:
            print("没有对局")
            time.sleep(2)
            clear()
        else:
            #还原对局
            for step in game_round:
                try:
                    if step["End"] == "Our_win":
                        print("玩家获胜")
                    elif step["End"] == "AI_win":
                        print("AI获胜")
                except:
                    #玩家
                    Our_step = step["Our"]
                    if Our_step == "stockpile":
                        print("玩家:攒子弹")
                    elif Our_step == "defense":
                        print("玩家:防御")
                    elif Our_step == "fight":
                        print("玩家:攻击")
                    elif Our_step == "Break_Defense":
                        print("玩家:攻击（破防）")

                    # AI
                    AI_step = step["AI"]
                    if AI_step == "stockpile":
                        print("AI:攒子弹")
                    elif AI_step == "defense":
                        print("AI:防御")
                    elif AI_step == "fight":
                        print("AI:攻击")
                    elif AI_step == "Break_Defense":
                        print("AI:攻击（破防）")

                    time.sleep(1)

                    print("")
            print("回车键退出")
            input()
            clear()

    elif what == "2":
        if game_round_retain == {}:
            print("没有已保存的对局")
            time.sleep(3)
            clear()
        else:
            what = input("请输入要查看第几场对局（你保存了"+str(game_nmu)+"局）")
            clear()
            try:
                round = game_round_retain[what]
                Times = (round)["time"]
                print(Times)
                print()
                time.sleep(1)
                for step in round["round"]:
                    try:
                        if step["End"] == "Our_win":
                            print("玩家获胜")
                        elif step["End"] == "AI_win":
                            print("AI获胜")
                    except:
                        # 玩家
                        Our_step = step["Our"]
                        if Our_step == "stockpile":
                            print("玩家:攒子弹")
                        elif Our_step == "defense":
                            print("玩家:防御")
                        elif Our_step == "fight":
                            print("玩家:攻击")
                        elif Our_step == "Break_Defense":
                            print("玩家:攻击（破防）")

                        # AI
                        AI_step = step["AI"]
                        if AI_step == "stockpile":
                            print("AI:攒子弹")
                        elif AI_step == "defense":
                            print("AI:防御")
                        elif AI_step == "fight":
                            print("AI:攻击")
                        elif AI_step == "Break_Defense":
                            print("AI:攻击（破防）")

                        time.sleep(1)

                        print("")
                print("回车键退出")
                input()
                clear()
            except:
                print("没有这个对局")
                time.sleep(3)
                clear()

#主体
#检查文件夹
user()

while True:
    if login_state:
        print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\n5.注销账号\n6.退出登录")
    else:
        print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\n5.注册\n6.登录")
    what = input()
    if what == "1":
        # 重置
        Our = "pass"
        AI = "pass"
        Our_power = 0
        AI_power = 0
        game_round.clear()

        print("游戏开始")

        #这里要给你的控制台的“全部清除”来个热键（我的是Shift+c）
        #清空内容
        time.sleep(1)
        clear()

        while True:
            #玩家部分
            # 由子弹数量来决定选项
            if int(Our_power) < int(Can_fight):
                what = input(
                    "请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(key_defense) + "）（你" + str(
                        Our_power) + "发子弹,但不够攻击）")
            elif int(Our_power) >= int(Can_fight) and int(Our_power) < int(Can_Break_Defense):
                what = input(
                    "请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(key_defense) + "）,攻击（输入" + str(
                        key_fight) + "）（你有" + str(Our_power) + "发子弹）")
            else:
                what = input(
                    "请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(key_defense) + "）,攻击（输入" + str(
                        key_fight) + "），攻击（有破防属性）（输入" + str(key_Break_Defense) + "）（你有" + str(
                        Our_power) + "发子弹）")

            # 根据玩家的选择来输出
            if what == str(key_stockpile):
                Our = "stockpile"
                Our_power += int(Can_stockpile)
                print("玩家:攒子弹")
            elif what == str(key_defense):
                Our = "defense"
                print("玩家:防御")
            elif what == str(key_fight) and Our_power >= int(Can_fight):
                Our = "fight"
                Our_power -= int(Can_fight)
                print("玩家:攻击")
            elif what == str(key_Break_Defense) and Our_power >= int(Can_Break_Defense):
                Our = "Break_Defense"
                Our_power -= int(Can_Break_Defense)
                print("玩家:攻击（破防）")
            else:
                angry = 0
                while True:
                    keyboard.release("shift+c")
                    if angry == 5:
                        print("不是哥们，重开吧")
                        time.sleep(2)
                        clear()
                        break
                    else:
                        print("不是哥们，你在干什么呀。")
                        if int(Our_power) < int(Can_fight):
                            what = input("请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(
                                key_defense) + "）（你没有子弹！）")
                        elif int(Our_power) >= int(Can_fight) and int(Our_power) < int(Can_Break_Defense):
                            what = input("请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(
                                key_defense) + "）,攻击（输入" + str(key_fight) + "）（你有" + str(Our_power) + "发子弹）")
                        else:
                            what = input("请选择攒子弹（输入" + str(key_stockpile) + "），防御（输入" + str(
                                key_defense) + "）,攻击（输入" + str(key_fight) + "），攻击（有破防属性）（输入" + str(
                                key_Break_Defense) + "）（你有" + str(Our_power) + "发子弹）")

                        if what == str(key_stockpile):
                            Our = "stockpile"
                            Our_power += int(Can_stockpile)
                            print("玩家:攒子弹")
                            break
                        elif what == str(key_defense):
                            Our = "defense"
                            print("玩家:防御")
                            break
                        elif what == str(key_fight) and Our_power >= int(Can_fight):
                            Our = "fight"
                            Our_power -= int(Can_fight)
                            print("玩家:攻击")
                            break
                        elif what == str(key_Break_Defense) and Our_power >= int(Can_Break_Defense):
                            Our = "Break_Defense"
                            Our_power -= int(Can_Break_Defense)
                            print("玩家:攻击（破防）")
                            break

                    angry += 1

                    if angry == 5:
                        break

            # AI部分
            AI = AI_choose(AI_power)
            if AI == "stockpile":
                AI_power += int(Can_stockpile)
                print("AI:攒子弹")
            elif AI == "defense":
                print("AI:防御")
            elif AI == "fight":
                AI_power -= int(Can_fight)
                print("AI:攻击")
            elif AI == "Break_Defense":
                AI_power -= int(Can_Break_Defense)
                print("AI:攻击（破防）")

            #回放功能
            game_round.append({"Our":str(Our),"AI":str(AI)})

            #判断输赢
            finale = Win_Lose(Our,AI)
            if finale == "Our_win":
                print("恭喜获胜")
                time.sleep(3)
                clear()
                # 回放功能
                game_round.append({"End": finale})
                break
            elif finale == "AI_win":
                print("可惜，人机赢了")
                time.sleep(3)
                clear()
                # 回放功能
                game_round.append({"End": finale})
                break
            elif finale == "Continue":
                time.sleep(2)
                clear()

        #保存对局
        what = input("保存对局？(y/n)")
        if what == "n":
            clear()
        if what == "y":
            game_nmu += 1
            t = time.localtime()
            Time = str(t.tm_year)+"年"+str(t.tm_mon)+"月"+str(t.tm_mday)+"日"+" "+str(t.tm_hour)+"时"+str(t.tm_min)+"分"+str(t.tm_sec)+"秒"
            game_round_retain[str(game_nmu)] = {"time":str(Time),"round":game_round}



    elif what == "2":
        print("已退出")
        break

    elif what == "3":
        clear()
        set()

    #对局查看
    elif what == "4":
        clear()
        view_match()

    else:
        clear()

"""
往期更新：
2.0.0
1.更换了pyautogui库为keyboard库，并更改了相关代码
2.若没有导入keyboard，会出现警告语

1.3.1
修复了一个bug：
菜单出现不明字符“”

代码:
print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\5.注销账号\6.退出登录")
                                                 ^         ^

print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\5.注册\6.登录")
                                                 ^     ^

在“5”和“6”前面添加“n”

1.3.0
1.添加了更新内容提示
2.初步编写登录功能的选项，未能正常使用
3.更改规则：只有双方为“破防”才能抵消

1.2.0
更新回放功能

1.1.1
修复一个bug：
如何子弹数量没有符合开枪或破防的数量时，则不能开枪

代码：
elif what == str(key_fight) and Our_power == int(Can_fight):
                                          ^^

elif what == str(key_Break_Defense) and Our_power == int(Can_Break_Defense):
                                                  ^^
把两处的“==”改为“>="

1.1.0
更新菜单与键位调节

1.0.0
编写主体代码

"""