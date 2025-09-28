import socket
import platform
import re
import cmd
import datetime
import threading
import time
import sys
import json
import base64
from random import randint

import tabulate
import requests

CONFIG_PATH = "config.json"

try:
    with open(CONFIG_PATH, "r+") as f:
        dic_tmp = json.load(f)
        ban_ip, ban_words, ban_length = dic_tmp['ban']['ip'], dic_tmp['ban']['words'], dic_tmp['ban']['length']
        status_enter_after_promis_tmp = dic_tmp['ENTER_AFTER_PROMISE']
        status_show_enter_message_tmp = dic_tmp['SHOW_ENTER_MESSAGE']
        status_auto_remove_offline = dic_tmp['AUTO_REMOVE_OFFLINE']
        if type(ban_ip) == type(list()) and type(ban_words) == type(list()) and type(ban_length) == type(int()) and type(status_enter_after_promis_tmp) == type(bool()) and type(status_show_enter_message_tmp) == type(bool()) and type(status_auto_remove_offline) == type(bool()):
            pass
        
        else:
            raise

        for v in ban_ip:
            if (type(v) != type(str())):
                raise
        
        for v in ban_words:
            if (type(v) != type(str())):
                raise
        
except:
    with open(CONFIG_PATH, "w+") as f:
        json.dump({
            "ban" : {
                "words" : [],
                "ip" : [],
                "length": 2147483647
            },
            "ENTER_AFTER_PROMISE" : False,
            "SHOW_ENTER_MESSAGE" : False,
            "AUTO_REMOVE_OFFLINE" : False
        }, f)

if len(sys.argv) == 4:
    ip = sys.argv[1]
    account_numbers = sys.argv[2]
    portin = sys.argv[3]
    try:
        account_numbers = int(account_numbers)
        portin = int(portin)
    except:
        print("[Error] 参数输入不正确")
        exit()

else:
    print("You can use the command `chat <IP> <MAXNUMBER> <PORT>` (with the prefix './' if needed) to start it.")
    ip = input("Connect to IP: ")
    account_numbers = eval(input("The maximum times of connecting: "))
    portin = eval(input("The connecting port (must be spare): "))

s = socket.socket()
s.bind((ip, portin))
s.listen(account_numbers)
s.setblocking(False)

VERSION = "v2.0.0"
s.setblocking(False)
NEWEST_VERSION = "UNKNOWN"

try:
    NEWEST_VERSION = requests.get("https://bopid.cn/chat/newest_version_chat.html").content.decode()
except:
    NEWEST_VERSION = "UNKNOWN"

def time_str() -> str:
    return str(datetime.datetime.now())

with open("./log.txt", "w+") as file:
    file.write(f"[{time_str()}] TouchFish(Server) started successfully, {ip}: {portin}.\n")

"""
conn:       链接操作口          [socket.socket()]
address:    IP                 [(str, int)]
username:   用户名、IP 对应     {str : str}
requestion: 申请加入队列        [(socket.socket(), (str, int)) or None]
"""
conn = []
address = []
username = dict()
if_online = dict()
requestion = []
msg_counts = dict()
admins = []
dic_config_file = json.load(open(CONFIG_PATH, "r+"))
ban_ip_lst = dic_config_file["ban"]["ip"]
ban_words_lst = dic_config_file["ban"]["words"]
ban_length = dic_config_file["ban"]["length"]
ENTER_AFTER_PROMISE = dic_config_file["ENTER_AFTER_PROMISE"]
AUTO_REMOVE_OFFLINE = dic_config_file["AUTO_REMOVE_OFFLINE"]


ENTER_HINT = ""
with open("hint.txt", "a+", encoding="utf-8") as file:
    file.seek(0)
    ENTER_HINT = file.read()
if not ENTER_HINT.split('\n'):
    ENTER_HINT = ""
if ENTER_HINT and ('\n' not in ENTER_HINT):
    ENTER_HINT += '\n'

if ENTER_HINT == "":
    ENTER_HINT = "（没有提示）"
print("您当前的进入提示是（注意使用的是 utf-8）：" + ENTER_HINT)
SHOW_ENTER_MESSAGE = dic_config_file["SHOW_ENTER_MESSAGE"]
EXIT_FLG = False 
flush_txt = ""

def send_all(msg : str):
    global conn
    for j in range(len(conn)):
        try:
            conn[j].send(bytes(msg, encoding="utf-8"))
            if_online[address[j][0]] = True
        except:
            if_online[address[j][0]] = False

def add_accounts():
    global flush_txt
    while True:
        if EXIT_FLG:
            return
        if (len(conn) > int(account_numbers)):
            print("注意：连接数已满")
            sys.stdout.flush()
            break
        conntmp = None
        addresstmp = None
        try:
            conntmp, addresstmp = s.accept()
        except:
            continue
        
        try:
            if ENTER_HINT:
                conntmp.send(bytes("[房主提示] " + ENTER_HINT, encoding="utf-8"))
        except:
            pass

        if addresstmp[0] in ban_ip_lst:
            continue
        
        if ENTER_AFTER_PROMISE:
            try:
                conntmp.send(bytes("[系统提示] 本聊天室需要房主确认后加入，请等待房主同意。\n", encoding="utf-8"))
            except:
                pass
            flush_txt += f"[{time_str()}] <{len(requestion)}> User {addresstmp} requested an entry to the chatting room.\n"
            print(f"\n<{len(requestion)}> 用户 {addresstmp} 申请加入聊天室，请处理。\n{ip}:{portin}> ", end="")
            sys.stdout.flush()
            requestion.append((conntmp, addresstmp))
            continue
        
        if SHOW_ENTER_MESSAGE:
            print(f"\n用户 {addresstmp} 加入聊天室！\n{ip}:{portin}> ", end="")
            sys.stdout.flush()


        if_online[addresstmp[0]] = True
        msg_counts[addresstmp[0]] = 0 
        flush_txt += f"[{time_str()}] User {addresstmp} has connected to server.\n"
        

        if platform.system() != "Windows":
            conntmp.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180 * 60)
            conntmp.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        else: 
            conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            conntmp.ioctl(socket.SIO_KEEPALIVE_VALS, (
                1, 180 * 1000, 30 * 1000
            ))
        conntmp.setblocking(False)
        conn.append(conntmp)
        address.append(addresstmp)
        username[addresstmp[0]] = "UNKNOWN"

def receive_msg():
    global conn
    global address
    global flush_txt
    while True:
        if EXIT_FLG:
            return
        for j in requestion:
            if j == None:
                continue
            try:
                tmp = j[0].recv(1024).decode('utf-8')
            except:
                pass

        for i in range(len(conn)):
            data = None
            try:
                data = conn[i].recv(1024).decode('utf-8')
            except:
                continue
            if address[i][0] in ban_ip_lst:
                continue
            if not data:
                continue
            msg_counts[address[i][0]] += 1
            if len(data) > ban_length:
                continue
            flg = False
            for v in ban_words_lst:
                if v in data:
                    flg = True
                    continue
            if flg:
                continue
            username_tmp = data.split(':')[0]
            if not ':' in data and '用户 ' in data and ' 加入聊天室。' in data:
                username_tmp = data.split('用户 ')[1]
                username_tmp = username_tmp.split(' 加入聊天室。')[0]
            else:
                username_tmp = "UNKNOWN"
            username[address[i][0]] = username_tmp
            flush_txt += f"[{time_str()}] User {address[i]} sent a massage: {data}"

            new_conn_lst = []
            new_add_lst = []

            for j in range(len(conn)):
                try:
                    conn[j].send(bytes(data, encoding="utf-8"))
                    if_online[address[j][0]] = True
                    if AUTO_REMOVE_OFFLINE:
                        new_conn_lst.append(conn[j])
                        new_add_lst.append(address[j])
                except:
                    if_online[address[j][0]] = False
                    continue

            if AUTO_REMOVE_OFFLINE:
                conn = new_conn_lst
                address = new_add_lst
 
admin_socket = None
class Server(cmd.Cmd):
    prompt = f"{ip}:{portin}> "
    intro = f"""欢迎来到 TouchFish！当前版本：{VERSION}，最新版本：{NEWEST_VERSION}
如果想知道有什么命令，请输入 help
具体的使用指南，参见 help <你想用的命令>。详细的使用指南，见 wiki：https://github.com/2044-space-elevator/TouchFish/wiki/How-to-use-chat.exe
注意：消息无法实时更新，需要输入 flush 命令将缓冲区输出到 ./log.txt。
永久配置文件位于目录下的 ./config.json"""
    def __init__(self):
        cmd.Cmd.__init__(self)
    
    def ban(self, arg : list, operator) -> str:
        OP_MSG = ""
        global ban_ip_lst
        global flush_txt
        global ban_words_lst
        global ban_length
        global dic_config_file


        arg = arg.split(' ')
        if len(arg) < 2:
            return "[Error] 参数错误\n"
        SAVE_CONFIG = False
        if arg[0] == 'forever':
            SAVE_CONFIG = True
            arg = arg[1:]
        
        att1 = ["ip", "words", "length"]
        if arg[0] not in att1:
            return "[Error] 参数错误\n"
        
        if arg[0] == 'ip':
            arg = arg[1:]
            for ip in arg:
                if SAVE_CONFIG:
                    dic_config_file["ban"]["ip"].append(ip)
                ban_ip_lst.append(ip)
                try:
                    send_all(f"[系统提示] {operator} 封禁了用户 {ip}, 用户名 {username[ip]}\n")
                except:
                    pass
            flush_txt += f"[{time_str()}] {operator} banned the user(s) from IP(s) {', '.join(arg)}.\n"
        
        if arg[0] == 'words':
            arg = arg[1:]
            for word in arg:
                if SAVE_CONFIG:
                    dic_config_file["ban"]["words"].append(word)
                ban_words_lst.append(word)
            flush_txt += f"[{time_str()}] {operator} banned the word(s) {', '.join(arg)}.\n"
        
        if arg[0] == "length":
            try:
                arg[1] = int(arg[1])
            except:
                return "[Error] 参数错误\n"
            send_all(f"[系统提示] {operator} 设置了发送信息的长度最大为 {arg[1]}。\n")
            if SAVE_CONFIG:
                dic_config_file["ban"]["length"] = arg[1]
            ban_length = arg[1]
            flush_txt += f"[{time_str()}] {operator} limited message length to: {ban_length}\n"

        dic_config_file["ban"]["ip"] = list(set(dic_config_file["ban"]["ip"]))
        dic_config_file["ban"]["words"] = list(set(dic_config_file["ban"]["words"]))

        ban_ip_lst = list(set(ban_ip_lst))
        ban_words_lst = list(set(ban_words_lst))

        if SAVE_CONFIG:
            with open(CONFIG_PATH, "w+") as f:
                json.dump(dic_config_file, f)

        return ""
    
    def enable(self, arg : list, operator) -> str:
        global ban_ip_lst
        global flush_txt
        global ban_words_lst
        global ban_length
        global dic_config_file

        arg = arg.split(' ')
        OP_MSG = ""
        if len(arg) < 2:
            return "[Error] 参数错误\n"

        SAVE_CONFIG = False
        if arg[0] == "forever":
            SAVE_CONFIG = True
            arg = arg[1:]
        
        att1 = ["ip", "words"]
        if arg[0] not in att1:
            return "[Error] 参数错误\n"

        if arg[0] == 'ip':
            arg = arg[1:]
            for ip in arg:
                if SAVE_CONFIG:
                    try:
                        dic_config_file["ban"]["ip"].remove(ip)
                    except:
                        pass
                try:
                    ban_ip_lst.remove(ip)
                    send_all(f"[系统提示] {operator} 解除封禁了 IP {ip}，用户名 {username[ip]}。\n")
                except:
                    pass
            flush_txt += f"[{time_str()}] {operator} unbanned the user(s) from IP(s) {', '.join(arg)}.\n"
        
        if arg[0] == 'words':
            arg = arg[1:]
            for word in arg:
                if SAVE_CONFIG:
                    try:
                        dic_config_file["ban"]["words"].remove(word)
                    except:
                        pass
                try:
                    ban_words_lst.remove(word)
                except:
                    pass
            flush_txt += f"[{time_str()}] {operator} unbanned the word(s) {', '.join(arg)}.\n"

        if SAVE_CONFIG:
            with open(CONFIG_PATH, "w+") as f:
                json.dump(dic_config_file, f)
        
        return ""

    def set(self, arg : list, operator) -> str:
        global flush_txt
        arg = arg.split(' ')
        if len(arg) != 2 and len(arg) != 3:
            return "[Error] 参数错误\n"

        att1 = ["EAP", "SEM", "ARO"]
        att2 = ["on", "off"]
        att3 = "forever"
        if (arg[0] not in att1) or (arg[1] not in att2):
            return "[Error] 参数错误\n"

        if len(arg) == 3 and arg[2] != att3:
            return "[Error] 参数错误\n"

        global ENTER_AFTER_PROMISE
        global SHOW_ENTER_MESSAGE
        global AUTO_REMOVE_OFFLINE
        global dic_config_file
        if arg[0] == "EAP":
            if arg[1] == "on":
                ENTER_AFTER_PROMISE = True
            else:
                ENTER_AFTER_PROMISE = False
            if len(arg) == 3:
                dic_config_file["ENTER_AFTER_PROMISE"] = ENTER_AFTER_PROMISE
        
        if arg[0] == "SEM":
            if arg[1] == "off":
                SHOW_ENTER_MESSAGE = False
            else:
                SHOW_ENTER_MESSAGE = True
            if len(arg) == 3:
                dic_config_file["SHOW_ENTER_MESSAGE"] = SHOW_ENTER_MESSAGE

        if arg[0] == 'ARO':
            if arg[1] == "off":
                AUTO_REMOVE_OFFLINE = False
            else:
                AUTO_REMOVE_OFFLINE = True
            if len(arg) == 3:
                dic_config_file["AUTO_REMOVE_OFFLINE"] = AUTO_REMOVE_OFFLINE
        
        flush_txt += f'[{time_str()}] {operator} set {arg[0]} as {arg[1]}'
        if len(arg) == 3:
            flush_txt += f" and saved it in the configuration."
            with open(CONFIG_PATH, "w+") as file:
                json.dump(dic_config_file, file)
        flush_txt += '\n'
        return ""

    def do_enable(self, arg):
        """
        使用方法（~ 表示 enable)：
            ~ ip <*ip1> <*ip2> ... <*ipK>   解禁这 K 个 IP
            ~ words <*w1> <*w2> ... <*wK>   删除这 K 个屏蔽词
            在 enable 命令的后面直接加 forever，可以使得本设置保存到配置文件。下一次启动本目录的 server 时能使用。
        """
        OP_MSG = self.enable(arg, "房主")
        print(OP_MSG, end="")
        
    def do_ban(self, arg):
        """
        使用方法（~ 表示 ban)：
            ~ ip <*ip1> <*ip2> ... <*ipK>   封禁这 K 个 IP
            ~ words <*w1> <*w2> ... <*wK>   添加这 K 个屏蔽词
            ~ length <*len>                 拒绝分发所有长度大于 len 的信息
            在 ban 命令的后面直接加 forever，可以使得本设置保存到配置文件。下一次启动本目录的 server 时能使用。
        """
        OP_MSG = self.ban(arg, "房主")
        print(OP_MSG, end="")

    def do_set(self, arg):
        """
        使用方法（~ 表示 set)：
            ~ EAP on/off 开启/关闭准许后进入
            ~ SEM on/off 开启/关闭进入后提示
            ~ ARO on/off 开启/关闭收发消息时删去离线接口（建议开启）
            你可以在命令后面加上 "forever"，表示将设置保存到配置文件。下一次启动本目录的 server 时能使用。
        """
        OP_MSG = self.set(arg, "房主")
        print(OP_MSG, end="")

    def print_user(self, userlist : "list[str]") -> str:
        header = ["IP", "USERNAME", "IS_ONLINE", "IS_BANNED", "SEND_TIMES"]
        data_body = []
        for ip in userlist:
            data_body.append([ip, username[ip], if_online[ip], ip in ban_ip_lst, msg_counts[ip]])
        return str(tabulate.tabulate(data_body, headers=header)) + '\n'

    def reject(self, rid : int, operator) -> str:
        OP_MSG = ""
        global flush_txt
        try:
            flush_txt += f"[{time_str()}] <{rid}> User {requestion[rid][1]} was rejected to enter in the chatting room.\n"
            OP_MSG += f"{operator}拒绝第 {rid} 号请求（用户 {requestion[rid][1]}。\n"
            requestion[rid][0].send(bytes(f"[系统提示] {operator} 被拒绝加入聊天室\n", encoding="utf-8"))
            requestion[rid] = None
        except:
            OP_MSG += f"[Error] 第 {rid} 次提示信息发送失败\n"
        return OP_MSG
    
    def accept(self, rid : int, operator) -> str:
        OP_MSG = ""
        global flush_txt
        if not requestion[rid]:
            OP_MSG += f"[Error] 第 {rid} 号进入请求已处理\n"
            return OP_MSG
        try:
            if_online[requestion[rid][1][0]] = True
            msg_counts[requestion[rid][1][0]] = 0
            username[requestion[rid][1][0]] = "UNKNOWN"
            requestion[rid][0].setblocking(0)


            if platform.system() != "Windows":
                requestion[rid][0].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180 * 60)
                requestion[rid][0].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
            else: 
                requestion[rid][0].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
                requestion[rid][0].ioctl(socket.SIO_KEEPALIVE_VALS, (
                    1, 180 * 1000, 30 * 1000
                ))

            conn.append(requestion[rid][0])
            address.append(requestion[rid][1])
            requestion[rid][0].send(bytes(f"[系统提示] {operator} 已准许您加入聊天室\n", encoding="utf-8"))
            flush_txt += f"[{time_str()}] <{rid}> User {requestion[rid][1]} was accepted to enter the chatting room.\n"
            OP_MSG += f"{operator}准许了第 {rid} 号请求，用户 {requestion[rid][1]} 进入聊天室。\n"
            requestion[rid] = None
        except:
            OP_MSG += f"[Error] 第 {rid} 次准许操作失败\n"
        return OP_MSG
    
    def accept_multi(self, arg, operator) -> str:
        arg = arg.split(' ')
        OP_MSG = ""
        for v in arg:
            try:
                i = int(v)
                if i >= len(requestion):
                    raise
                if not requestion[i]:
                    raise
            except:
                OP_MSG += "[Error] 参数错误或请求已被处理\n"
                return OP_MSG
            
        for v in arg:
            OP_MSG += self.accept(int(v), operator)

        OP_MSG += ""
        return OP_MSG

    def do_accept(self, arg):
        """
        使用方法（~ 表示 accept）：
            ~ <rid1> <rid2> <rid3> ... <ridK> 准许第 rid1, rid2, rid3, ..., ridK 号进入请求
        """
        OP_MSG = self.accept_multi(arg, "房主")
        print(OP_MSG, end="")
    
    def reject_multi(self, arg, operator) -> str:
        OP_MSG = ""
        arg = arg.split(' ')
        for i in arg:
            try:
                i = int(i)
                if i >= len(requestion):
                    raise
                if not requestion[i]:
                    raise
            except:
                return "[Error] 参数错误或请求已被处理\n"
        for i in arg:
            OP_MSG += self.reject(int(i), operator)
        OP_MSG += ""
        return OP_MSG

    def do_reject(self, arg):
        """
        使用方法（~ 表示 reject）：
            ~ <rid1> <rid2> <rid3> ... <ridK> 拒绝第 rid1, rid2, rid3, ..., ridK 号进入请求
        """
        OP_MSG = self.reject_multi(arg, "房主")
        print(OP_MSG, end="")
    
    def broadcast(self, arg, operator):
        OP_MSG = ""
        global flush_txt
        flush_txt += f"[{time_str()}] {operator} broadcasted msg '{arg}'\n"
        for j in range(len(conn)):
            try:
                conn[j].send(bytes(f"[{operator}广播] " + arg + '\n', encoding="utf-8"))
                if_online[address[j][0]] = True
            except:
                OP_MSG += f"向用户 {address[j]} (用户名 {username[address[j][0]]}) 广播失败。\n"
                if_online[address[j][0]] = False
                continue
        OP_MSG += "广播成功。\n"
        return OP_MSG

    def do_broadcast(self, arg):
        """
        使用方法（~ 表示 broadcast)：
            ~ <msg> 向全体成员广播信息 msg
        """    
        OP_MSG = self.broadcast(arg, "房主")
        print(OP_MSG, end="")

    def search(self, arg):
        OP_MSG = ""
        attributes = ["ip", "user", "online", "offline", "send_times", "banned"]
        arg = arg.split(' ')
        if (arg[0] not in attributes):
            return "[Error] 参数错误\n"

        search_lst = []
        if (arg[0] == 'ip'):
            if len(arg) != 2:
                return "[Error] 参数错误\n"
            search_lst.append(arg[1])
        
        if arg[0] == "user":
            if len(arg) != 2:
                return "[Error] 参数错误\n"
            for i in address:
                ip = i[0]
                if re.search(arg[1], username[ip]):
                    search_lst.append(ip)
        
        if arg[0] == "online":
            for i in address:
                ip = i[0]
                if if_online[ip]:
                    search_lst.append(ip)
            search_lst.sort(key=lambda x : msg_counts[x]) 
            search_lst.reverse()
        
        if arg[0] == 'offline':
            for i in address:
                ip = i[0]
                if not if_online[ip]:
                    search_lst.append(ip)
        
        if arg[0] == "banned":
            for i in address:
                ip = i[0]
                if ip in ban_ip_lst:
                    search_lst.append(ip)
            OP_MSG += self.print_user(search_lst) + '\n'
            return OP_MSG
        
        if arg[0] == "send_times":
            if len(arg) != 2:
                return "[Error] 参数错误\n"
            try:
                arg[1] = int(arg[1])
                if arg[1] < 0:
                    raise
            except:
                return "[Error] <*times> 必须是非负整数\n"
            for i in address:
                ip = i[0]
                if msg_counts[ip] >= arg[1]:
                    search_lst.append(ip)
            search_lst = list(set(search_lst))
            search_lst.sort(key = lambda x : msg_counts[x])
            search_lst.reverse()
            OP_MSG += self.print_user(search_lst) + '\n'
            return OP_MSG
        
        search_lst = list(set(search_lst))
        return self.print_user(search_lst) + '\n'
        
    def do_search(self, arg):
        """
        使用方法（~ 表示 search）：
            ~ ip <*ip>              搜索所有 IP 为 *ip 的用户信息，支持正则。
            ~ user <*user>          搜索所有 username 为 *user 的用户信息（支持正则）
            ~ online                搜索所有在线的用户的信息
            ~ offline               搜索所有离线的用户的信息
            ~ banned                查询所有被 ban 的用户的信息   
            ~ send_times <*times>   搜索所有发送信息次数大于等于 times 的用户的信息（按发送次数从大到小输出）
        """ 
        OP_MSG = self.search(arg)
        print(OP_MSG, end="")

    def do_flush(self, arg):
        """
        输出缓冲区内容
        """
        global flush_txt
        with open("./log.txt", "a+", encoding="utf-8") as file:
            file.write(flush_txt)
        flush_txt = ""
    
    def do_exit(self, arg):
        """
        退出当前程序
        """
        self.do_flush(...)
        global EXIT_FLG
        EXIT_FLG = 1
        exit()
    
    def do_admin(self, arg):
        """
        多管理员模式
        ~ on 开启多管理员模式
        ~ off 关闭多管理员模式
        ~ add <ip1> <ip2> ... <ipK> 允许 <ip1>, <ip2>, ..., <ipK> 成为管理员
        ~ remove <ip1> <ip2> ... <ipK> 将 <ip1>, <ip2>, ..., <ipK> 从管理员中移除
        """
        global admin_socket
        global admins

        arg = arg.split(' ')
        if len(arg) == 1:
            arg = arg[0]
            if arg == "on":
                try:
                    admin_socket = socket.socket()
                    port = 11451
                    while True:
                        try:
                            admin_socket.bind((ip, port))
                            break
                        except:
                            port = randint(10000, 65535)
                    admin_socket.listen(10000)
                    admin_socket.setblocking(0)
                    print(f"管理员模式开启成功！指令端口 {ip}:{port}。")
                except:
                    print("[Error] 开启失败")
            
            elif arg == "off":
                if admin_socket:
                    admin_socket.close()
                admin_socket = None
            
            else:
                print("[Error] 参数错误")
            return
        if arg[0] == "add":
            for i in range(1, len(arg)):
                admins.append(arg[i])
        
        elif arg[0] == "remove":
            new_admins = []
            for i in range(len(admins)):
                if admins[i] in arg:
                    continue
                new_admins.append(admins[i])
            admins = list(new_admins)
        
        else:
            print("[Error] 参数错误")

admin_conns = []
admin_address = []
admin_name = dict()
last_sent = time.time()
def admin_accept():
    global admin_conns
    global admin_address
    global flush_txt
    global last_sent
    while True:
        if EXIT_FLG:
            return

        if not admin_socket:
            continue

        newconn = []
        newaddress = []
        for i in range(len(admin_conns)):
            if admin_address[i] not in admins:
                continue
            if time.time() - last_sent > 20:
                try:
                    admin_conns[i].send(bytes("{'type' : 'test', 'message' : None }", encoding="utf-8"))
                except:
                    continue
            newconn.append(admin_conns[i])
            newaddress.append(admin_address[i])
        if time.time() - last_sent > 20:
            last_sent = time.time()
        admin_conns = list(newconn)
        admin_address = list(newaddress)

        try:
            conntmp, addresstmp = admin_socket.accept()
        except:
            continue
        
        if not addresstmp[0] in admins:
            continue
        
        flush_txt += f"[{time_str()}] Administrator {addresstmp} entered.\n"
        print(f"\n管理员 {addresstmp} 进入管理平台。\n{ip}:{portin}> ", end="")
        conntmp.setblocking(0)
        if platform.system() != "Windows":
            conntmp.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180 * 60)
            conntmp.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        else: 
            conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            conntmp.ioctl(socket.SIO_KEEPALIVE_VALS, (
                1, 180 * 1000, 30 * 1000
            ))
        admin_address.append(addresstmp[0])
        admin_conns.append(conntmp)
        admin_name[addresstmp[0]] = None

def admin_deal():
    pass

server = Server()

threading.Thread(target=server.cmdloop).start()
threading.Thread(target=receive_msg).start()
threading.Thread(target=add_accounts).start()
threading.Thread(target=admin_accept).start()
