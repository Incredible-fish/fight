'''
版本：3.1.0

更新内容：
1.编写了获取旧版本代码界面，也可在该界面手动监测更新
2.从3.2.0开始，若是代码是被旧版本代码获取的，将不会在监测更新，最新版本不受影响(可在设置中取消暂停监测)
3.优化了更新时的重启
4.解决了设置的局部修改全局变量的报错

'''
import random
import time
import os
import re
import json
import html
import ast

#如果下载了第三方库，就可以游玩游戏
Can_paly_game = True
#如果下载第三方库，就可以自动更新
Update = True

#这个你要导入
try:
    import keyboard
except:
    what = input("你没有导入 “keyboard”，程序可能会报错。请问是否下载？（y/n[除y任意键]）")
    if what == "y":
        os.system("pip install keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple")
        import keyboard
    else:
        Can_paly_game = False

try:
    import requests
except:
    what = input("你没有导入 “requests”，自动监测更新功能将无法使用。请问是否下载？（y/n[除y任意键]）")
    if what == "y":
        os.system("pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")
        import requests
    else:
        Update = False


#清屏快捷键
def clear():
    if Can_paly_game:
        keyboard.press("shift+c")
        keyboard.release("shift+c")
        time.sleep(0.1)
    else:
        pass

#fight库
fight_list = ["fight3.2.0","fight3.1.0","fight3.0.0","fight2.1.0","fight2.0.0","fight0.0.0"]

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

#Behavioral_index值精确到小数点后几位，若后面有零，则自动省略
precision_for_Behavioral_index = 3
#决定了collation_probability输出时精确到小数点后几位，过大会影响计算机的运算能力：若后面有零，则自动省略
precision_for_collation_probability = 3

#难度
difficulty = "esay"

#关于存放用户信息的文件夹
def user():
    if os.path.exists("user"):
        pass
    else:
        os.mkdir("user")

#由子弹数量来决定选项
def our_choose():
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
    return what

#聪明点的AI的部分功能整合
class hight_AI_function:
    #定义变量
    def __init__(self,round,AI_power,Our_power,Can_Break_Defense):
        self.AI_power = AI_power
        self.Our_power = Our_power
        self.round = round
        self.Can_Break_Defense = Can_Break_Defense

    #根据指数来影响选择
    def Behavioral_index(self):
        part = float((self.AI_power-self.Our_power)/self.Can_Break_Defense)
        overall = float((self.AI_power+self.Our_power)/2/self.Can_Break_Defense)
        Behavioral_index = round(part * overall * (10**precision_for_Behavioral_index))/(10**precision_for_Behavioral_index)
        return Behavioral_index

    #整理round
    def tidy_up(self):
        new_round = []
        for now in range(0,len(self.round)):
            new_round.append(self.round[now]["Our"])
        self.round = new_round

    #检查重复
    def check_duplicate(self, duplicate_round=[]):
        outcome = {"repeat_item":[],"prediction":""}

        if duplicate_round == []:
            #循环查找重复
            #rounds 寻找重复的项数
            for rounds in range(1,5):
                #如果self.round的长度没有rounds+1,则跳过
                if len(self.round) < rounds+1:
                    pass
                else:
                    #如果self.round的长度大于两倍的rounds时，find_round 为self.round的最后rounds两倍数量的项
                    if len(self.round) >= rounds*2:
                        find_round = self.round[-rounds*2:]
                        convenient_run = True
                    #反之，find_round为self.round本身
                    else:
                        find_round = self.round
                        convenient_run = False
                    #特殊情况
                    if rounds == 1:
                        preceding = find_round[0]
                        latter_item = find_round[1]
                        if latter_item == preceding:
                            outcome["repeat_item"] = preceding
                            if len(preceding) == len(latter_item):
                                outcome["prediction"] = preceding[0]
                            # 反之截取latter_item长度加一的项
                            else:
                                outcome["prediction"] = preceding[len(latter_item) + 1]
                    else:
                        #开始在find_round循环查找重复 roundss为来到find_round的那个位置
                        if convenient_run:
                            rounded = rounds
                        else:
                            rounded = len(find_round)-rounds
                        for roundss in range(0,rounded):
                            #preceding 固定长度为rounds
                            preceding = find_round[roundss:roundss+rounds]
                            #latter_item 为剩下的内容
                            latter_item = find_round[roundss+rounds:]
                            #Contrasts_Items 从头截取latter_item长度的项，用于比较是否重复
                            contrasts_items = preceding[:len(latter_item)]
                            if latter_item == contrasts_items:
                                outcome["repeat_item"] = preceding
                                #如果preceding和latter_item长度相同，截取preceding的第一个项
                                if len(preceding) == len(latter_item):
                                    outcome["prediction"] = preceding[0]
                                #反之截取latter_item长度加一的项
                                else:
                                    outcome["prediction"] = preceding[len(latter_item)]

        else:
            outcome["repeat_item"] = duplicate_round
            #length 为duplicate_round的长度
            length = len(duplicate_round)
            #如果self.round没有两倍的length,则find_round为self.round本身
            if len(self.round) < 2*length:
                find_round = self.round
            #反之为self.round的最后两倍的length项
            else:
                find_round = self.round[-2*length:]
            #开始在find_round循环查找重复
            for rounds in range(1,length+1):
                #contrasts 为self.round 的最后rounds项
                contrasts_items = self.round[-rounds:]
                #original_item 为duplicate_round的前rounds项·
                original_item = duplicate_round[:rounds]
                if contrasts_items == original_item:
                    # 如果contrasts_items和original_item长度相同，截取original_item的第一个项
                    if len(contrasts_items) == length:
                        outcome["prediction"] = duplicate_round[0]
                    # 反之截取rounds加一的项
                    else:
                        outcome["prediction"] = duplicate_round[rounds]

        return outcome

    #整理每个选项的概率
    def collation_probability(self,
                              probability={"stockpile_increases_probability": 0, "defense_increases_probability": 0,
                                           "fight_increases_probability": 0,
                                           "Break_Defense_increases_probability": 0},
                              can={"figh": False, "Break_Defense": False}):

        sums = 0
        new_probability = {"stockpile_increases_probability": 0, "defense_increases_probability": 0,
                           "fight_increases_probability": 0, "Break_Defense_increases_probability": 0}

        if not can["Break_Defense"]:
            if "Break_Defense_increases_probability" in probability:
                del probability["Break_Defense_increases_probability"]
            if "Break_Defense_increases_probability" in new_probability:
                del new_probability["Break_Defense_increases_probability"]

        if not can["fight"]:
            if "fight_increases_probability" in probability:
                del probability["fight_increases_probability"]
            if "fight_increases_probability" in new_probability:
                del new_probability["fight_increases_probability"]

        for key in probability.keys():
            probabilitys = probability[key]
            sums += 1 + probabilitys
            new_probability[key] = 1 + probabilitys

        for key in probability.keys():
            probabilitys = new_probability[key]
            new_probability[key] = round(probabilitys / sums * (10 ** precision_for_collation_probability))

        return new_probability







#聪明点的AI的选择
def hight_AI_chose(AI_power,round,Our_power,Can_Break_Defensed = Can_Break_Defense):
    AI = hight_AI_function(AI_power,round,Our_power,Can_Break_Defensed)
    Behavioral_index_number = AI.Behavioral_index()







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
    global Can_fight,Can_Break_Defense,Can_stockpile,key_Break_Defense,key_defense,key_fight,key_stockpile

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

    try:
        with open("Stop_old_automatic_update","r",encoding="utf-8") as f:
            what = f.read()
            Stop_old_automatic_update_list = ast.literal_eval(what)
            if os.path.basename(__file__) in Stop_old_automatic_update_list:
                print("请问是否开启监测代码更新（y/跳过请键入其他键或直接回车）")
                what = input()
                if what == "y":
                    Stop_old_automatic_update_list.remove(os.path.basename(__file__))
                    write_in = str(Stop_old_automatic_update_list)
                    with open("Stop_old_automatic_update","w",encoding="utf-8") as fs:
                        fs.write(write_in)
                else:
                    pass
            else:
                pass
    except FileNotFoundError:
        pass
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

#菜单功能 7.获取旧版本fight
def get_fight_other():
    #获取当前文件夹内的fight文件
    fight_lists = ""
    file_list = os.listdir(os.path.abspath('.'))
    for file_list_nmu in range(0,len(file_list)):
        fight_lists = fight_lists + file_list[file_list_nmu] + ","
    fight_re_test = r"fight\d{1}.??\.\d{1}.??\.\d{1}.??"
    fight_file_all = re.findall(fight_re_test,fight_lists)

    #获取远程代码库
    try:
        url = "https://pastebin.com/hJdgvVfe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        htmls = response.text
        re_txt = r'<div class="de1">.+</div></li>'
        find_code = re.findall(re_txt,htmls,re.S)
        remote_code = find_code[0][17:len(find_code)-12]
        remote_code = remote_code.replace("&quot;","\"")
        fihgt_all_req = json.loads(remote_code,strict = False)
        fihgt_all_req_version = list(fihgt_all_req.keys())

    except requests.exceptions.RequestException :
        print("网络请求失败：请检查是否连接网络")
        time.sleep(1)
        clear()
        return None

    #排除已下载的版本
    for file_list_nmu in range(0,len(fight_file_all)):
        if fight_file_all[file_list_nmu] in fihgt_all_req_version:
            fihgt_all_req_version.remove(fight_file_all[file_list_nmu])

    what = input(f"已找到一下版本的fight:\n{fihgt_all_req_version}\n请输入你要下载的版本(按任意键退出)")
    if "fight"+what in fihgt_all_req_version:
        fight_get = "fight"+what
        fight_get_Information = fihgt_all_req[fight_get][1]
        fight_get_Download = fihgt_all_req[fight_get][0]
        what = input(f"以下是版本{fight_get}描述：\n{fight_get_Information}\n是否下载？（y/n(除y任意键)）")
        if what == "y":
            try:
                code = automatic_update_find_code(fight_get_Download)
                # 生成文件
                temp_file = f"{fight_get}.py"
                with open(temp_file, 'w', encoding="utf-8") as f:
                    f.write(code)
                if fight_get != fihgt_all_req_version[0]:
                    with open("Stop_old_automatic_update","w+",encoding="utf-8") as f:
                        what = f.read()
                        if what == "" or what == "[]":
                            write_in = f"[\"{fight_get}.py\"]"
                            f.write(write_in)
                        else:
                            Stop_old_automatic_update_list = ast.literal_eval(what)
                            Stop_old_automatic_update_list.append(f"{fight_get}.py")
                            write_in = str(Stop_old_automatic_update_list)
                            f.write(write_in)
                else:
                    pass
                what = input("已成功下载成功，重新启动？（y）不重新启动？（除y任意键）")
                # 重启脚本
                if what == "y":
                    current_file_directory = os.path.abspath('.')
                    os.system(str(current_file_directory) + "/" + str(temp_file))
                    keyboard.press("shift+f10")
                    keyboard.release("shift+f10")
                    keyboard.press('ctrl+f2')
                    keyboard.release('ctrl+f2')
                    now_file_name = os.path.basename(__file__)
                    for when in range(0, len(now_file_name) - 3):
                        keyboard.press(now_file_name[when])
                        keyboard.release(now_file_name[when])
                    keyboard.press("Enter")
                    keyboard.release("Enter")
                else:
                    print("已退出")
                    clear()
                    return None
            except requests.exceptions.ConnectionError:
                clear()
                print("未连接网络")
                return None
            except requests.exceptions.ConnectTimeout:
                clear()
                print("连接超时")
                return None

    else:
        clear()
        print("已退出")
        return None





#自动更新
def automatic_update_find_code(url,Connect_timeout=3,Read_timeout=3):
    urls = url
    rep = requests.get(urls, timeout=(Connect_timeout,Read_timeout))
    htmls = rep.text
    htmles = htmls.replace("\r\n", "\n")
    re_txt = r'<code role="code" class="language-txt">.+</code>'
    find_code = re.findall(re_txt,htmls,re.S)[0]
    code = find_code[39:len(find_code)-7]
    code = html.unescape(code)
    return code

def automatic_update():
    try:
        url = "https://pastebin.com/hJdgvVfe"

        # 获取远程代码库
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        htmls = response.text
        re_txt = r'<div class="de1">.+</div></li>'
        find_code = re.findall(re_txt,htmls,re.S)
        remote_code = find_code[0][17:len(find_code)-12]
        remote_code = remote_code.replace("&quot;","\"")
        fihgt_all_req = json.loads(remote_code,strict = False)

        #监测是否有新版本
        fihgt_all_req_version = list(fihgt_all_req.keys())
        if fihgt_all_req_version == fight_list:
            print("无需更新")
            return None
        else:
            fight_new = fihgt_all_req_version[0]
            fight_new_Information = fihgt_all_req[fight_new][1]
            fight_new_Download = fihgt_all_req[fight_new][0]
            what = input(f"发现新版本{fight_new},以下是版本描述：\n{fight_new_Information}\n是否下载？（y/n(除y任意键)）")
            if what == "y":
                try:
                    code = automatic_update_find_code(fight_new_Download)
                    # 生成文件
                    temp_file = f"{fight_new}.py"
                    with open(temp_file, 'w', encoding="utf-8") as f:
                        f.write(code)
                    what = input("已成功更新成功，不重新启动？（除a/y任意键）重新启动但不删除旧版本？（a）重新启动并删除旧版本？(y)")
                    if what != "a" and what != "y":
                        return None
                    else:
                        # 重启脚本
                        current_file_directory = os.path.abspath('.')
                        os.system(str(current_file_directory)+"/"+str(temp_file))
                        if what == "y":
                            with open("Stop_automatic_update","w",encoding="utf-8") as f:
                                f.write("")
                        keyboard.press("shift+f10")
                        keyboard.release("shift+f10")
                        keyboard.press('ctrl+f2')
                        keyboard.release('ctrl+f2')
                        now_file_name = os.path.basename(__file__)
                        for when in range(0,len(now_file_name)-3):
                            keyboard.press(now_file_name[when])
                            keyboard.release(now_file_name[when])
                        keyboard.press("Enter")
                        keyboard.release("Enter")
                        if what == "y":
                            os.remove(__file__)
                except requests.exceptions.ConnectionError:
                    print("未连接网络")
                    return None
                except requests.exceptions.ConnectTimeout:
                    print("连接超时")
                    return None

    except requests.exceptions.RequestException :
        print("网络请求失败：请检查是否连接网络")

#主体
#检查文件夹
user()

time.sleep(1)
# 如何没有导入库，将无法使用程序
if Can_paly_game:
    clear()
else:
    print("你跳过了下载必须库，将无法正常运行游戏，正在退出")

if Update and Can_paly_game:
    try:
        with open("Stop_old_automatic_update","r",encoding="utf-8") as f:
            what = f.read()
            Stop_old_automatic_update_list = ast.literal_eval(what)
            if os.path.basename(__file__) in Stop_old_automatic_update_list:
                print("已跳过监测")
            else:
                automatic_update()
    except:
        if "Stop_automatic_update" in os.listdir(os.path.abspath('.')):
            print("已跳过更新")
            os.remove(str(os.path.abspath('.'))+"/"+"Stop_automatic_update")
        else:
            automatic_update()
else:
    print("你跳过了下载requests，将无法监测更新")

while True:
    if not(Can_paly_game):
        break

    if login_state:
        print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\n5.注销账号\n6.退出登录\n7.获取其他版本")
    else:
        print("你要干嘛\n1.开始游戏\n2.退出\n3.设置\n4.查看对局\n5.注册\n6.登录\n7.获取其他版本")
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
            # 玩家部分
            # 由子弹数量来决定选项
            what = our_choose()
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
                while True:
                    clear()
                    what = our_choose()
                    keyboard.release("shift+c")
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

    #获取其他版本的代码
    elif what == "7":
        clear()
        get_fight_other()

    else:
        clear()

"""
往期更新：

3.1.0
1.添加了清华镜像源，加快了下载库的速度
2.从3.1.0开始，更新后不会在二次监测更新

3.0.0
1.初步编写了高级AI
2.对代码的anger功能删减
3.编写了自动监测更新模块
4.完善了导入库的问题

2.2.0
1.整理了部分代码

2.1.0
1.整理了部分代码

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
