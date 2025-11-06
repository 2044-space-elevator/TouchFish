# now just test

import socket
import time
from sys import exit, argv
import threading
import json
import cmd
import os

result_event = threading.Event()
result_msg = None

"""
# 该功能以后实现
if __name__ == "__main__":
    try:
        if len(argv) - 1 > 0 and (argv[1] == "-h" or argv[1] == "--help" or argv[2] == "-h" or argv[2] == "--help"): # argv[2] 照顾 python admin.py
            admin = Admin()
            admin.do_help("")
            os._exit(0)
    except:
        print("参数错误，不要多余参数")
        os._exit(1)
"""

IP = input("Connect to IP:")
PORT = input("Connect to PORT:")
ADMIN_NAME = input("Username:")

CURRENT_VERSION = "beta-20251004"

try:
    PORT = int(PORT)
except:
    print("输入错误。")
    exit()

s = socket.socket()
s.connect((IP, PORT))
s.setblocking(False)

CONNECT_TIME = time.time()
while True:
    if time.time() - CONNECT_TIME > 40:
        print("服务器连接失败")
        exit()
    
    try:
        msg_str = s.recv(1024).decode("utf-8")
    except:
        continue
    msg = json.loads(msg_str)
    if msg["type"] == "test":
        print("连接成功！")
        break

s.send(bytes(json.dumps({"type" : "username", "message" : ADMIN_NAME}), encoding="utf-8"))

EXIT_FLG = False

def send_msg(typ : str, arg : str):
    global result_msg
    result_event.clear()
    try:
        s.send(bytes(json.dumps({"type": typ, "message": arg}), encoding="utf-8"))
    except:
        print("发送失败！\n", end="")
        return
    
    result_event.wait(timeout=10)
    if result_msg:
        print('\n' + result_msg, end="")
    result_msg = None

def receive_ret():
    global EXIT_FLG, result_msg
    while True:
        time.sleep(0.1)
        if EXIT_FLG:
            exit()
            break
        msg_str = None
        if not msg_str:
            continue
        try:
            msg = json.loads(msg_str)
        except Exception as err:
            with open("admin_err.log", "a+") as file:
                file.write("JSON 解析错误：" + str(err) + "\n")
            continue
        if msg["type"] == "removed":
            print("\n\n你已被服务器移除出管理员列表！")
            os._exit(1)
        if msg["type"] == "server_closed":
            print("\n\n服务器已关闭！")
            os._exit(0)
        if msg["type"] == "result":
            result_msg = msg["message"]
            result_event.set()

class Admin(cmd.Cmd):
    prompt = f"{IP}:{PORT} (admin)> "
    intro = f"""详细的使用指南，见 wiki：https://github.com/2044-space-elevator/TouchFish/wiki/How-to-use-admin (基本命令相同，但是没有 admin 命令)
可以使用 cmd type admin_err.log 查看错误日志 (Windows) 或 cmd cat admin_err.log (Linux)。（当然一般不会有错误）
当前版本：{CURRENT_VERSION}，为测试版，可能会有一些问题。
其余懒得写了，看 server 里的吧"""

    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_broadcast(self, arg):
        send_msg("broadcast", arg)
    
    def do_ban(self, arg):
        send_msg("ban", arg)
    
    def do_enable(self, arg):
        send_msg("enable", arg)
    
    def do_set(self, arg):
        send_msg("set", arg)
    
    def do_exit(self, arg):
        global EXIT_FLG
        EXIT_FLG = True
        exit()
    
    def do_accept(self, arg):
        send_msg("accept", arg)
    
    def do_reject(self, arg):
        send_msg("reject", arg)
    
    def do_search(self, arg):
        send_msg("search", arg)
    
    def do_req(self, arg):
        """
        查询加入请求（其余命令详见 wiki）
        """
        send_msg("req", arg)

    def do_cmd(self, arg):
        """
        使用方法 (~ 表示 cmd):
            ~ <cmd> 执行这个系统命令，并输出结果
        """
        if not arg.strip():
            print("[ERROR] 参数错误")
            return
        try:
            result = os.system(arg)
            if result:
                print("[ERROR] Command failed! Return code: " + str(result))
        except Exception as err:
            print("命令执行失败！错误信息:", err)

if __name__ == "__main__":
    tr = threading.Thread(target=receive_ret)
    tr.start()
    admin = Admin()
    tr2 = threading.Thread(target=admin.cmdloop)
    tr2.start()
    admin = Admin()
