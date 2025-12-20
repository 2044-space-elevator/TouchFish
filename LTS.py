# TouchFish LTS Client/Server Unified Program (Version 4)





# ============================== 第一部分：常量和变量定义 ==============================





import base64
import datetime
import json
import os
import platform
import queue
import re
import socket
import sys
import threading
import time

VERSION = "v4.1.0"

RESULTS = \
{
	"IP is banned": "您的 IP 被服务端封禁。",
	"Room is full": "服务端连接数已满，无法加入。",
	"Duplicate usernames": "该用户名已被占用，请更换用户名。",
	"Username consists of banned words": "用户名中包含违禁词，请更换用户名。"
}

COLORS = \
{
	"black": 0,
	"red": 1,
	"green": 2,
	"yellow": 3,
	"blue": 4,
	"magenta": 5,
	"cyan": 6,
	"white": 7
}

DEFAULT_CLIENT_CONFIG = {"side": "Client", "ip": "127.0.0.1", "port": 8080, "username": "user"}

DEFAULT_SERVER_CONFIG = \
{
	"side": "Server",
	"general": {"server_ip": "127.0.0.1", "server_port": 8080, "server_username": "root", "max_connections": 128},
	"ban": {"ip": [], "words": []},
	"gate": {"enter_hint": "", "enter_check": False},
	"message": {"allow_private": True, "max_length": 16384},
	"file": {"allow_any": True, "allow_private": True, "max_size": 1048576}
}

CONFIG_TYPE_CHECK_TABLE = \
{
	"general.server_ip": "str", "general.server_port": "int", "general.server_username": "str", "general.max_connections": "int",
	"ban.ip": "list", "ban.words": "list",
	"gate.enter_hint": "str", "gate.enter_check": "bool",
	"message.allow_private": "bool", "message.max_length": "int",
	"file.allow_any": "bool", "file.allow_private": "bool", "file.max_size": "int"
}

CONFIG_LIST = \
"""
参数名称                   当前值      修改示例       描述

ban.ip                     <1>         ["8.8.8.8"]    IP 黑名单
ban.words                  <2>         ["a", "b"]     屏蔽词列表

gate.enter_hint            <3>         "Hi there!\\n"  进入提示
gate.enter_check           {!s:<12}True           加入是否需要人工放行

message.allow_private      {!s:<12}False          是否允许私聊
message.max_length         {:<12}256            最大消息长度（字节）

file.allow_any             {!s:<12}False          是否允许发送文件
file.allow_private         {!s:<12}False          是否允许发送私有文件
file.max_size              {:<12}16384          最大文件大小（字节）

为了防止尖括号处的内容写不下，此处单独列出：
<1>:
{}
<2>:
{}
<3>:
{}
"""[1:-1]

HELP_HINT_1 = \
"""
聊天室界面分为输出模式和输入模式，默认为输出模式，此时行首没有符号。
按下回车键即可从输出模式转为输入模式，此时行首有一个 > 符号。
按下 Enter（或输入任意指令）即可从输入模式转换回输出模式。
输出模式下，输入的指令将被忽略，且不会显示在屏幕上。
输入模式下，新的消息将等待到退出输入模式才会显示。
聊天室内可用的指令有：
"""[1:-1]

HELP_HINT_2 = \
"""
        dashboard                    展示聊天室各项数据
        distribute <filename>        发送文件
        exit                         退出或关闭聊天室
        help                         显示本帮助文本
        send                         发送多行消息
        send <message>               发送单行消息
        transfer <uid> <filename>    向某个用户发送私有文件
        whisper <uid>                向某个用户发送多行私聊消息
        whisper <uid> <message>      向某个用户发送单行私聊消息
      * ban ip add <ip>              封禁 IP 或 IP 段
      * ban ip remove <ip>           解除封禁 IP 或 IP 段
      * ban words add <word>         屏蔽某个词语
      * ban words remove <word>      解除屏蔽某个词语
      * broadcast                    向全体用户广播多行消息
      * broadcast <message>          向全体用户广播单行消息
      * config <key> <value>         修改聊天室配置项
      * doorman accept <uid>         通过某个用户的加入申请
      * doorman reject <uid>         拒绝某个用户的加入申请
      * kick <uid>                   踢出某个用户
     ** admin add <uid>              添加管理员
     ** admin remove <uid>           移除管理员
     ** save                         保存聊天室配置项信息
"""[1:-1]

HELP_HINT_3 = \
"""
标注 * 的指令只有状态为 Admin 或 Root 的用户可以使用。
标注 ** 的指令只有状态为 Root 的用户可以使用。
对于 dashboard 指令，状态为 Root 的用户可以看到所有用户的 IP 地址，其他用户不能。
对于 ban ip 指令，支持输入形如 a.b.c.d/e 的 IP 段，但 CIDR (e 值) 不得小于 24。
对于 config 指令，<key> 的格式以 dashboard 指令输出的参数名称为准。
对于 config 指令，<value> 的格式以 dashboard 指令输出的修改示例为准。
对于 kick 指令，状态为 Root 的用户可以踢出状态为 Admin 或 Online 的用户。
对于 kick 指令，状态为 Admin 的用户只能踢出状态为 Online 的用户。
对于 kick 指令，状态为 Admin 的用户只能踢出状态为 Online 的用户。
"""[1:-1]

WEBPAGE_CONTENT = \
"""
HTTP/1.1 405 Method Not Allowed
Content-Type: text/html; charset=utf-8
my_socket: close

<html>
<head><meta name="color-scheme" content="light dark"><meta charset="utf-8"><title>警告 Warning</title></head>

<body>
<h1>405 Method Not Allowed</h1>
<pre style="word-wrap: break-word; white-space: pre-wrap; color: red; font-weight: bold;">
您似乎正在使用浏览器或类似方法向 TouchFish 服务器发送请求。
此类请求可能会危害 TouchFish 服务器的正常运行，因此请不要继续使用此访问方法，否则我们可能会封禁您的 IP 地址。
正确的访问方法是，使用 TouchFish 生态下任意兼容的 TouchFish Client 登录 TouchFish Server。
欲了解更多有关 TouchFish 聊天室的信息，请访问 TouchFish 聊天室的官方 Github 仓库：
<a href="https://github.com/2044-space-elevator/TouchFish">github.com/2044-space-elevator/TouchFish</a>

Seemingly you are sending requests to TouchFish Server via something like Web browsers.
Such requests are HAZARDOUS to the server and will result in a BAN if you insist on this access method.
To use the TouchFish chatroom service correctly, you might need a dedicated TouchFish Client.
For more information, please visit the official Github repository of this project:
<a href="https://github.com/2044-space-elevator/TouchFish">github.com/2044-space-elevator/TouchFish</a>
</pre>
</body>
</html>
"""[1:]

config = DEFAULT_SERVER_CONFIG
blocked = False
my_username = "user"
my_uid = 0
file_order = 0
my_socket = None
users = []
s = socket.socket()
side = "Server"
server_version = VERSION
log_queue = queue.Queue()
receive_queue = queue.Queue()
send_queue = queue.Queue()
print_queue = queue.Queue()
history = []
online_count = 1
first_data = None
buffer = ""
EXIT_FLAG = False





# ================================ 第二部分：功能性函数 ================================





def ring():
	print('\a', end="", flush=True)

def clear_screen():
	if platform.system() == 'Windows':
		os.system('cls')
	else:
		os.system('clear')

def enter():
	print("请输入要发送的消息。")
	print("输入结束后，先按下 Enter，然后按下 Ctrl + C。")
	message = ""
	while True:
		try:
			message += input() + "\n"
		except EOFError:
			break
	if message:
		message = message[:-1]
	return message

def dye(text, color_code):
	if color_code:
		return "\033[0m\033[1;3{}m{}\033[8;30m".format(COLORS[color_code], text)
	return text

def flush():
	global print_queue
	if not blocked:
		while not print_queue.empty():
			print(print_queue.get())

def prints(text, color_code=None):
	global print_queue
	if not blocked:
		print(dye(text, color_code))
	else:
		print_queue.put(dye(text, color_code))

def printf(text, color_code=None):
	print(dye(text, color_code))

def printc(verbose, text):
	if verbose:
		print(dye(text, "black"))

def check_ip_segment(element):
	if not '/' in element:
		element = element + "/32"
	pattern = r'^(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)$'
	match = re.search(pattern, element)
	if not match:
		return []
	for i in range(1, 5):
		if int(match.group(i)) < 0 or int(match.group(i)) > 255:
			return []
	if int(match.group(5)) < 0 or int(match.group(5)) > 32:
		return []
	if int(match.group(5)) < 24:
		return [""]
	if int(match.group(4)) % 2 ** (32 - int(match.group(5))):
		return []
	result = []
	for i in range(int(match.group(4)), int(match.group(4)) + 2 ** (32 - int(match.group(5)))):
		result.append("{}.{}.{}.{}".format(int(match.group(1)), int(match.group(2)), int(match.group(3)), i))
	return result

def check_ip(element):
	pattern = r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$'
	match = re.search(pattern, element)
	if not match:
		return False
	for i in range(1, 5):
		if int(match.group(i)) < 0 or int(match.group(i)) > 255:
			return False
	return True

def time_str():
	return str(datetime.datetime.now())

def announce(uid):
	first_line = dye("[" + str(datetime.datetime.now())[11:19] + "]", "black")
	if uid == my_uid:
		first_line += dye(" [您发送的]", "blue")
	first_line += dye(" [公告]", "red")
	first_line += " "
	first_line += dye("@", "black")
	first_line += dye(users[uid]['username'], "yellow")
	first_line += dye(":", "black")
	prints(first_line)

def print_message(message):
	first_line = dye("[" + message['time'][11:19] + "]", "black")
	if message['from'] == my_uid:
		first_line += dye(" [您发送的]", "blue")
	if message['to'] == my_uid:
		first_line += dye(" [发给您的]", "blue")
	try:
		if message['filename']:
			first_line += dye(" [文件]", "red")
	except KeyError:
		pass
	if message['to'] == -2:
		first_line += dye(" [广播]", "red")
	if message['to'] >= 0:
		first_line += dye(" [私聊]", "green")
	first_line += " "
	first_line += dye("@", "black")
	first_line += dye(users[message['from']]['username'], "yellow")
	if message['to'] >= 0:
		first_line += dye(" -> ", "green")
		first_line += dye("@", "black")
		first_line += dye(users[message['to']]['username'], "yellow")
	first_line += dye(":", "black")
	prints(first_line)
	try:
		if message['filename']:
			if side == "Client":
				try:
					if platform.system() == "Windows":
						with open("TouchFishFiles\\{}.file".format(message['order']), 'wb') as f:
							f.write(base64.b64decode(message['content']))
					else:
						with open("TouchFishFiles/{}.file".format(message['order']), 'wb') as f:
							f.write(base64.b64decode(message['content']))
				except:
					pass
			prints("发送了文件 {}，已经保存到：TouchFishFiles/{}.file".format(message['filename'], message['order']), "cyan")
		else:
			prints(message['content'], "white")
	except KeyError:
		prints(message['content'], "white")

def process(message):
	global users
	global online_count
	global EXIT_FLAG
	ring()
	if message['type'] == "CHAT.RECEIVE":
		message['time'] = str(datetime.datetime.now())
		print_message(message)
		return
	if message['type'] == "GATE.CLIENT_REQUEST.ANNOUNCE":
		announce(0)
		prints("用户 {} (UID = {}) 请求加入聊天室，请求结果：".format(message['username'], message['uid']) + message['result'], "cyan")
		if side == "Client":
			users.append({'username': message['username'], 'status': "Rejected"})
			if message['result'] == "Pending review":
				users[message['uid']]['status'] = "Pending"
			if message['result'] == "Accepted":
				users[message['uid']]['status'] = "Online"
				if side == "Client":
					online_count += 1
		return
	if message['type'] == "GATE.STATUS_CHANGE.ANNOUNCE":
		announce(message['operator'])
		prints("用户 {} (UID = {}) 的状态变更为：".format(users[message['uid']]['username'], message['uid']) + message['status'], "cyan")
		if side == "Client":
			users[message['uid']]['status'] = message['status']
			if message['status'] in ["Offline", "Kicked"]:
				online_count -= 1
		if message['uid'] == my_uid and message['status'] == "Kicked":
			while blocked:
				pass
			prints("您被踢出了聊天室。", "cyan")
			prints("\033[0m\033[1;36m再见！\033[0m")
			time.sleep(1)
			EXIT_FLAG = True
			exit()
	if message['type'] == "SERVER.CONFIG.CHANGE":
		announce(message['operator'])
		prints("配置项 {} 变更为：".format(message['key']) + str(message['value']), "cyan")
		if side == "Client":
			config[message['key'].split('.')[0]][message['key'].split('.')[1]] = message['value']
		return
	if message['type'] == "SERVER.STOP.ANNOUNCE":
		if side == "Client":
			announce(0)
			prints("聊天室服务端已经关闭。", "cyan")
			prints("\033[0m\033[1;36m再见！\033[0m")
			time.sleep(1)
			EXIT_FLAG = True
			exit()

def read():
	global my_socket
	global buffer
	while True:
		try:
			my_socket.setblocking(False)
			chunk = my_socket.recv(65536).decode('utf-8')
			if not chunk:
				break
			buffer += chunk
		except BlockingIOError:
			break
	return None

def get_message():
	global buffer
	message = ""
	while not message:
		try:
			message, buffer = buffer.split('\n', 1)
		except:
			return None
	try:
		return json.loads(message)
	except:
		return None





# ============================= 第三部分：与指令对应的函数 =============================





def do_broadcast(arg, message=None, verbose=True, by=-1):
	global history
	global log_queue
	global send_queue
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]['status'] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	if message == None:
		if arg:
			message = arg
		else:
			message = enter()
	if side == "Server":
		log_queue.put(json.dumps({'type': 'CHAT.LOG', 'time': time_str(), 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': -2}))
		history.append({'time': time_str(), 'from': by, 'content': message, 'to': -2})
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'CHAT.RECEIVE', 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': -2}}))
	if side == "Client":
		my_socket.send(bytes(json.dumps({'type': 'CHAT.SEND', 'filename': "", 'content': message, 'to': -2}) + "\n", encoding="utf-8"))
	printc(verbose, "操作成功。")

def do_doorman(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global online_count
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]['status'] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(' ', 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	try:
		arg[1] = int(arg[1])
	except:
		printc(verbose, "参数错误：UID 必须是整数。")
		return
	if not arg[0] in ['accept', 'reject']:
		printc(verbose, "参数错误：第一个参数必须是 accept 和 reject 中的某一项。")
		return
	if arg[1] <= -1 or arg[1] >= len(users):
		printc(verbose, "UID 输入错误。")
		return
	if users[arg[1]]['status'] != "Pending":
		printc(verbose, "只能对状态为 Pending 的用户操作。")
		if users[arg[1]]['status'] in ["Online", "Admin", "Root"] and arg[0] == "reject":
			printc(verbose, "您似乎想要踢出该用户，请使用以下指令：kick {}".format(arg))
		return
	
	if arg[0] == "accept":
		if side == "Server":
			send_queue.put(json.dumps({'to': arg[1], 'content': {'type': 'GATE.REVIEW_RESULT', 'accepted': True, 'operator': {'username': users[by]['username'], 'uid': by}}}))
			log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Online', 'uid': arg[1], 'operator': by}))
			for i in range(len(users)):
				if users[i]['status'] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Online', 'uid': arg[1], 'operator': by}}))
			users[arg[1]]['status'] = "Online"
			users_abstract = []
			for i in range(len(users)):
				users_abstract.append({"username": users[i]['username'], "status": users[i]['status']})
			send_queue.put(json.dumps({'to': arg[1], 'content': {'type': 'SERVER.DATA', 'server_version': VERSION, 'uid': arg[1], 'config': config, 'users': users_abstract, 'chat_history': history}}))
		if side == "Client":
			my_socket.send(bytes(json.dumps({'type': 'GATE.STATUS_CHANGE.REQUEST', 'status': 'Online', 'uid': arg[1]}) + "\n", encoding="utf-8"))
	
	if arg[0] == "reject":
		if side == "Server":
			users[arg[1]]['status'] = "Rejected"
			users[arg[1]]['body'].send(bytes(json.dumps({'type': 'GATE.REVIEW_RESULT', 'accepted': False, 'operator': {'username': users[by]['username'], 'uid': by}}) + "\n", encoding="utf-8"))
			log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Rejected', 'uid': arg[1], 'operator': by}))
			for i in range(len(users)):
				if users[i]['status'] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Rejected', 'uid': arg[1], 'operator': by}}))
			users[arg[1]]['body'].close()
			online_count -= 1
		if side == "Client":
			my_socket.send(bytes(json.dumps({'type': 'GATE.STATUS_CHANGE.REQUEST', 'status': 'Rejected', 'uid': arg[1]}) + "\n", encoding="utf-8"))
	
	printc(verbose, "操作成功。")

def do_kick(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global online_count
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]['status'] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	if not arg:
		printc(verbose, "参数错误：应当给出恰好 1 个参数。")
		return
	try:
		arg = int(arg)
	except:
		printc(verbose, "参数错误：UID 必须是整数。")
		return
	if arg <= -1 or arg >= len(users):
		printc(verbose, "UID 输入错误。")
		return
	if not users[arg]['status'] in ["Online", "Admin"]:
		printc(verbose, "只能对状态为 Online 或 Admin 的用户操作。")
		if users[arg]['status'] == "Pending":
			printc(verbose, "您似乎想要拒绝该用户的加入申请，请使用以下指令：doorman reject {}".format(arg))
		return
	if users[by]['status'] == "Admin" and users[arg]['status'] == "Admin":
		printc(verbose, "状态为 Admin 的用户只能对状态为 Online 的用户操作。")
		return
	if side == "Server":
		log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Kicked', 'uid': arg, 'operator': by}))
		users[arg]['status'] = "Kicked"
		try:
			users[arg]['body'].send(bytes(json.dumps({'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Kicked', 'uid': arg, 'operator': by}) + "\n", encoding="utf-8"))
		except:
			pass
		users[arg]['body'].close()
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Kicked', 'uid': arg, 'operator': by}}))
		online_count -= 1
	if side == "Client":
		my_socket.send(bytes(json.dumps({'type': 'GATE.STATUS_CHANGE.REQUEST', 'status': 'Kicked', 'uid': arg}) + "\n", encoding="utf-8"))
	printc(verbose, "操作成功。")

def do_admin(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	if by == -1:
		by = my_uid
	if users[by]['status'] != "Root":
		printc(verbose, "只有处于 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(' ', 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	if not arg[0] in ['add', 'remove']:
		printc(verbose, "参数错误：第一个参数必须是 add 或 remove。")
		return
	try:
		arg[1] = int(arg[1])
	except:
		printc(verbose, "参数错误：UID 必须是整数。")
		return
	if arg[1] <= 0 or arg[1] >= len(users):
		printc(verbose, "UID 输入错误。")
		return
	
	if arg[0] == 'add':
		if users[arg[1]]['status'] != "Online":
			printc(verbose, "只能对状态为 Online 的用户操作。")
			return
		users[arg[1]]['status'] = "Admin"
		log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Admin', 'uid': arg[1], 'operator': by}))
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Admin', 'uid': arg[1], 'operator': by}}))
	
	if arg[0] == 'remove':
		if users[arg[1]]['status'] != "Admin":
			printc(verbose, "只能对状态为 Admin 的用户操作。")
			return
		users[arg[1]]['status'] = "Online"
		log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Online', 'uid': arg[1], 'operator': by}))
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Online', 'uid': arg[1], 'operator': by}}))
	
	printc(verbose, "操作成功。")

def do_config(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global config
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]['status'] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	if verbose:
		arg = arg.split(' ', 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	if not arg[0] in CONFIG_TYPE_CHECK_TABLE:
		printc(verbose, "该参数不存在。")
		return
	if arg[0].split('.')[0] == "general":
		printc(verbose, "不允许在指令行内修改该参数，请退出聊天室后重新打开以修改。")
		return
	if verbose:
		if arg[0] == "gate.enter_hint":
			printc(verbose, "请注意，本参数修改时 <value> 需要带引号并转义。")
			printc(verbose, "例如，将进入提示设为英文 Hi there! 并且末尾换行：")
			printc(verbose, r'  config gate.enter_hint "Hi there!\n"')
			if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ['y', 'Y']:
				return
			print("\033[8;30m", end="")
		if arg[0] == "ban.ip" or arg[0] == "ban.words":
			printc(verbose, "请注意，本参数修改时 <value> 需要带引号并转义。")
			printc(verbose, "例如，将 fuck 和 shit 设置为屏蔽词：")
			printc(verbose, r'  config ban.words ["fuck", "shit"]')
			printc(verbose, "该操作将【清空】原有的屏蔽词列表（或 IP 黑名单），请谨慎操作！")
			if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ['y', 'Y']:
				return
			print("\033[8;30m", end="")
	
	try:
		if not eval("isinstance({}, {})".format(arg[1], CONFIG_TYPE_CHECK_TABLE[arg[0]])):
			printc(verbose, "输入数据的类型与参数不匹配。")
			raise
		if CONFIG_TYPE_CHECK_TABLE[arg[0]] == "int" and int(arg[1]) < 1:
			printc(verbose, "输入的数值必须是正整数。")
			raise
		if arg[0] == "message.max_length" and int(arg[1]) > 16384:
			printc(verbose, "允许的消息长度不得大于 16384。")
			raise
		if arg[0] == "file.max_size" and int(arg[1]) > 1073741824:
			printc(verbose, "允许的文件大小不得大于 1073741824。")
			raise
		if CONFIG_TYPE_CHECK_TABLE[arg[0]] == "list":
			for item in eval(arg[1]):
				if not isinstance(item, str):
					printc(verbose, "列表中的元素必须是 str（字符串）类型。")
					raise
			if len(eval(arg[1])) != len(set(eval(arg[1]))):
				printc(verbose, "列表中不能出现重复元素。")
				raise
		if arg[0] == "ban.words":
			for item in eval(arg[1]):
				if '\n' in item or '\r' in item or not item:
					printc(verbose, "屏蔽词列表中不能出现空串和换行符。")
					raise
		if arg[0] == "ban.ip":
			for item in eval(arg[1]):
				if not check_ip(item):
					printc(verbose, "IP 黑名单中的元素 {} 不是有效的点分十进制格式 IPv4 地址。".format(item))
					raise
		
		first, second = arg[0].split('.')
		if side == "Server":
			config[first][second] = eval(arg[1])
			log_queue.put(json.dumps({'type': 'SERVER.CONFIG.LOG', 'time': time_str(), 'key': first + '.' + second, 'value': eval(arg[1]), 'operator': by}))
			for i in range(len(users)):
				if users[i]['status'] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.CONFIG.CHANGE', 'key': first + '.' + second, 'value': eval(arg[1]), 'operator': by}}))
		printc(verbose, "操作成功。")
		if side == "Client":
			my_socket.send(bytes(json.dumps({'type': 'SERVER.CONFIG.POST', 'key': first + '.' + second, 'value': eval(arg[1])}) + "\n", encoding="utf-8"))
	except:
		printc(verbose, "指令格式不正确，请重试。")
		return

def do_ban(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global config
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]['status'] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(' ', 2)
	if len(arg) != 3:
		printc(verbose, "参数错误：应当给出恰好 3 个参数。")
		return
	if not arg[0] in ['ip', 'words']:
		printc(verbose, "参数错误：第一个参数必须是 ip 和 words 中的某一项。")
		return
	if not arg[1] in ['add', 'remove']:
		printc(verbose, "参数错误：第二个参数必须是 add 和 remove 中的某一项。")
		return
	
	if arg[0] == 'ip':
		ips = check_ip_segment(arg[2])
		if ips == []:
			printc(verbose, "输入数据不是合法的点分十进制格式 IPv4 地址或 IPv4 段。")
			return
		if ips == [""]:
			printc(verbose, "出于性能、安全性和实际使用环境考虑，IPv4 段的 CIDR 不得小于 24。")
			return
		
		if arg[1] == 'add':
			if side == "Server":
				ips = [item for item in ips if item not in config['ban']['ip']]
				config['ban']['ip'] += ips
				log_queue.put(json.dumps({'type': 'SERVER.CONFIG.LOG', 'time': time_str(), 'key': 'ban.ip', 'value': config['ban']['ip'], 'operator': by}))
				for i in range(len(users)):
					if users[i]['status'] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.CONFIG.CHANGE', 'key': 'ban.ip', 'value': config['ban']['ip'], 'operator': by}}))
			if side == "Client":
				ips = [item for item in ips if item not in config['ban']['ip']]
				new_value = config['ban']['ip'] + ips
				my_socket.send(bytes(json.dumps({'type': 'SERVER.CONFIG.POST', 'key': 'ban.ip', 'value': new_value}) + "\n", encoding="utf-8"))
			printc(verbose, "操作成功，共计封禁了 {} 个 IP 地址。".format(len(ips)))
		
		if arg[1] == 'remove':
			if side == "Server":
				ips = [item for item in ips if item in config['ban']['ip']]
				config['ban']['ip'] = [item for item in config['ban']['ip'] if not item in ips]
				log_queue.put(json.dumps({'type': 'SERVER.CONFIG.LOG', 'time': time_str(), 'key': 'ban.ip', 'value': config['ban']['ip'], 'operator': by}))
				for i in range(len(users)):
					if users[i]['status'] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.CONFIG.CHANGE', 'key': 'ban.ip', 'value': config['ban']['ip'], 'operator': by}}))
			if side == "Client":
				ips = [item for item in ips if item in config['ban']['ip']]
				new_value = [item for item in config['ban']['ip'] if not item in ips]
				my_socket.send(bytes(json.dumps({'type': 'SERVER.CONFIG.POST', 'key': 'ban.ip', 'value': new_value}) + "\n", encoding="utf-8"))
			printc(verbose, "操作成功，共计解除封禁了 {} 个 IP 地址。".format(len(ips)))
	
	if arg[0] == 'words':
		if '\n' in arg[2] or '\r' in arg[2] or not arg[2]:
			printc(verbose, "屏蔽词不能为空串，且不能包含换行符。")
			return
		if ' ' in arg[2]:
			if verbose:
				printc(verbose, "请注意，您输入的屏蔽词包含空格。")
				printc(verbose, "系统读取到的屏蔽词为（不包含开头的 ^ 符号和结尾的 $ 符号）：")
				printc(verbose, "^", arg[2], "$", sep="")
				if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ['y', 'Y']:
					return
				print("\033[8;30m", end="")
		
		if arg[1] == 'add':
			if arg[2] in config['ban']['words']:
				printc(verbose, "该屏蔽词已经在列表中出现了。")
				return
			if side == "Server":
				config['ban']['words'].append(arg[2])
				log_queue.put(json.dumps({'type': 'SERVER.CONFIG.LOG', 'time': time_str(), 'key': 'ban.words', 'value': config['ban']['words'], 'operator': by}))
				for i in range(len(users)):
					if users[i]['status'] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.CONFIG.CHANGE', 'key': 'ban.words', 'value': config['ban']['words'], 'operator': by}}))
			if side == "Client":
				new_value = config['ban']['words']
				new_value.append(arg[2])
				my_socket.send(bytes(json.dumps({'type': 'SERVER.CONFIG.POST', 'key': 'ban.words', 'value': new_value}) + "\n", encoding="utf-8"))
			printc(verbose, "操作成功。")
		
		if arg[1] == 'remove':
			if not arg[2] in config['ban']['words']:
				printc(verbose, "该屏蔽词不在列表中。")
				return
			if side == "Server":
				config['ban']['words'].remove(arg[2])
				log_queue.put(json.dumps({'type': 'SERVER.CONFIG.LOG', 'time': time_str(), 'key': 'ban.words', 'value': config['ban']['words'], 'operator': by}))
				for i in range(len(users)):
					if users[i]['status'] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.CONFIG.CHANGE', 'key': 'ban.words', 'value': config['ban']['words'], 'operator': by}}))
			if side == "Client":
				new_value = config['ban']['words']
				new_value.remove(arg[2])
				my_socket.send(bytes(json.dumps({'type': 'SERVER.CONFIG.POST', 'key': 'ban.words', 'value': new_value}) + "\n", encoding="utf-8"))
			printc(verbose, "操作成功。")

def do_send(arg, message=None, verbose=True, by=-1):
	global history
	global log_queue
	global send_queue
	global my_socket
	if by == -1:
		by = my_uid
	if message == None:
		if arg:
			message = arg
		else:
			message = enter()
	if not message:
		printc(verbose, "发送失败：消息不能为空。")
		return
	if len(message) > config['message']['max_length']:
		printc(verbose, "发送失败：消息太长。")
		return
	for word in config['ban']['words']:
		if word in message:
			printc(verbose, "发送失败：消息中包含屏蔽词：" + word)
			return
	if side == "Server":
		log_queue.put(json.dumps({'type': 'CHAT.LOG', 'time': time_str(), 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': -1}))
		history.append({'time': time_str(), 'from': by, 'content': message, 'to': -1})
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'CHAT.RECEIVE', 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': -1}}))
	if side == "Client":
		my_socket.send(bytes(json.dumps({'type': 'CHAT.SEND', 'filename': "", 'content': message, 'to': -1}) + "\n", encoding="utf-8"))
	printc(verbose, "发送成功。")

def do_whisper(arg, message=None, verbose=True, by=-1):
	global log_queue
	global send_queue
	global my_socket
	if by == -1:
		by = my_uid
	if not config['message']['allow_private']:
		printc(verbose, "此聊天室目前不允许发送私聊消息。")
		return
	try:
		arg, message = arg.split(' ', 1)
	except:
		pass
	try:
		arg = int(arg)
		if arg <= -1 or arg >= len(users):
			raise
	except:
		printc(verbose, "UID 输入错误。")
		return
	if not users[arg]['status'] in ["Online", "Admin", "Root"]:
		printc(verbose, "只能向状态处于 Online、Admin、Root 中的某一项的用户发送私聊消息。")
		return
	if arg == by:
		printc(verbose, "不能向自己发送私聊消息。")
		return
	if message == None:
		message = enter()
	if not message:
		printc(verbose, "发送失败：消息不能为空。")
		return
	if len(message) > config['message']['max_length']:
		printc(verbose, "发送失败：消息太长。")
		return
	for word in config['ban']['words']:
		if word in message:
			printc(verbose, "发送失败：消息中包含屏蔽词：" + word)
			return
	if side == "Server":
		log_queue.put(json.dumps({'type': 'CHAT.LOG', 'time': time_str(), 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': arg}))
		for i in range(len(users)):
			if users[i]['status'] in ["Admin", "Root"] or i == by or i == arg:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'CHAT.RECEIVE', 'from': by, 'order': 0, 'filename': "", 'content': message, 'to': arg}}))
	if side == "Client":
		my_socket.send(bytes(json.dumps({'type': 'CHAT.SEND', 'filename': "", 'content': message, 'to': arg}) + "\n", encoding="utf-8"))
	printc(verbose, "发送成功。")

def do_distribute(arg, message=None, verbose=True, by=-1):
	global log_queue
	global send_queue
	global my_socket
	global file_order
	if by == -1:
		by = my_uid
	if not config['file']['allow_any']:
		printc(verbose, "此聊天室目前不允许发送文件。")
		return
	for word in config['ban']['words']:
		if word in arg:
			printc(verbose, "发送失败：文件名中包含屏蔽词：" + word)
			return
	if not message:
		try:
			with open(arg, 'rb') as f:
				file_data = f.read()
			message = base64.b64encode(file_data).decode('utf-8')
		except:
			printc(verbose, "无法读取对应文件。")
			return
	if len(message) * 3 // 4 > config['file']['max_size']:
		printc(verbose, "发送失败：文件太大。")
		return
	if side == "Server":
		file_order += 1
		try:
			if platform.system() == "Windows":
				with open("TouchFishFiles\\{}.file".format(file_order), 'wb') as f:
					f.write(base64.b64decode(message))
			else:
				with open("TouchFishFiles/{}.file".format(file_order), 'wb') as f:
					f.write(base64.b64decode(message))
		except:
			pass
		if platform.system() == "Windows":
			tmp_filename = "TouchFishFiles\\{}.file".format(file_order)
		else:
			tmp_filename = "TouchFishFiles/{}.file".format(file_order)
		log_queue.put(json.dumps({'type': 'CHAT.LOG', 'time': time_str(), 'from': by, 'order': file_order, 'filename': arg, 'content': "", 'to': -1}))
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'CHAT.RECEIVE', 'from': by, 'order': file_order, 'filename': arg, 'content': tmp_filename, 'to': -1}}))
	if side == "Client":
		token = json.dumps({'type': 'CHAT.SEND', 'filename': arg, 'content': message, 'to': -1}) + "\n"
		chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
		for chunk in chunks:
			while True:
				try:
					my_socket.send(bytes(chunk, encoding="utf-8"))
					break
				except BlockingIOError:
					continue
				except Exception as e:
					printc(verbose, "发送失败：{}".format(e))
					return
	printc(verbose, "发送成功。")

def do_transfer(arg, message=None, verbose=True, by=-1):
	global log_queue
	global send_queue
	global my_socket
	global file_order
	if by == -1:
		by = my_uid
	arg = arg.split(' ', 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	if not config['file']['allow_any']:
		printc(verbose, "此聊天室目前不允许发送文件。")
		return
	if not config['file']['allow_private']:
		printc(verbose, "此聊天室目前不允许发送私有文件。")
		return
	try:
		arg[0] = int(arg[0])
		if arg[0] <= -1 or arg[0] >= len(users):
			raise
	except:
		printc(verbose, "UID 输入错误。")
		return
	if not users[arg[0]]['status'] in ["Online", "Admin", "Root"]:
		printc(verbose, "只能向状态处于 Online、Admin、Root 中的某一项的用户发送私有文件。")
		return
	if arg[0] == by:
		printc(verbose, "不能向自己发送私有文件。")
		return
	for word in config['ban']['words']:
		if word in arg[1]:
			printc(verbose, "发送失败：文件名中包含屏蔽词：" + word)
			return
	print(arg[1])
	if not message:
		try:
			with open(arg[1], 'rb') as f:
				file_data = f.read()
			message = base64.b64encode(file_data).decode('utf-8')
		except:
			printc(verbose, "无法读取对应文件。")
			return
	if len(message) * 3 // 4 > config['file']['max_size']:
		printc(verbose, "发送失败：文件太大。")
		return
	if side == "Server":
		file_order += 1
		try:
			if platform.system() == "Windows":
				with open("TouchFishFiles\\{}.file".format(file_order), 'wb') as f:
					f.write(base64.b64decode(message))
			else:
				with open("TouchFishFiles/{}.file".format(file_order), 'wb') as f:
					f.write(base64.b64decode(message))
		except:
			pass
		if platform.system() == "Windows":
			tmp_filename = "TouchFishFiles\\{}.file".format(file_order)
		else:
			tmp_filename = "TouchFishFiles/{}.file".format(file_order)
		log_queue.put(json.dumps({'type': 'CHAT.LOG', 'time': time_str(), 'from': by, 'order': file_order, 'filename': arg[1], 'content': "", 'to': arg[0]}))
		for i in range(len(users)):
			if users[i]['status'] in ["Admin", "Root"] or i == by or i == arg[0]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'CHAT.RECEIVE', 'from': by, 'order': file_order, 'filename': arg[1], 'content': tmp_filename, 'to': arg[0]}}))
	if side == "Client":
		token = json.dumps({'type': 'CHAT.SEND', 'filename': arg[1], 'content': message, 'to': arg[0]}) + "\n"
		chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
		for chunk in chunks:
			while True:
				try:
					my_socket.send(bytes(chunk, encoding="utf-8"))
					break
				except BlockingIOError:
					continue
				except Exception as e:
					printc(verbose, "发送失败：{}".format(e))
					return
	printc(verbose, "发送成功。")

def do_dashboard(arg=None):
	printf("=" * 76, "black")
	printf("服务端版本：" + server_version, "black")
	printf("您的 UID：" + str(my_uid), "black")
	printf("在线人数：{} / {}".format(online_count, config['general']['max_connections']), "black")
	printf("聊天室参数及具体用户信息详见下表。", "black")
	printf("=" * 76, "black")
	printf(CONFIG_LIST.format(config['gate']['enter_check'], config['message']['allow_private'], config['message']['max_length'], config['file']['allow_any'], config['file']['allow_private'], config['file']['max_size'], config['ban']['ip'], config['ban']['words'], config['gate']['enter_hint']), "black")
	printf("=" * 76, "black")
	if 'ip' in users[0]:
		printf(" UID  IP                        状态      用户名", "black")
		for i in range(len(users)):
			printf("{:>4}  {:<26}{:<10}{}".format(i, "{}:{}".format(users[i]['ip'][0], users[i]['ip'][1]), users[i]['status'], users[i]['username']), "black")
	else:
		printf(" UID  状态      用户名", "black")
		for i in range(len(users)):
			printf("{:>4}  {:<10}{}".format(i, users[i]['status'], users[i]['username']), "black")
	printf("=" * 76, "black")

def do_save(arg=None):
	global log_queue
	if users[my_uid]['status'] != "Root":
		print(users[my_uid]['status'])
		print("只有处于 Root 状态的用户有权执行该操作。")
		return
	try:
		with open("config.json", "w", encoding="utf-8") as f:
			json.dump(config, f)
		print("参数已经成功保存到配置文件 config.json，下次启动时将自动加载配置项。")
		log_queue.put(json.dumps({'type': 'SERVER.CONFIG.SAVE', 'time': time_str()}))
	except:
		print("无法将参数保存到配置文件 config.json，请稍后重试。")

def do_exit(arg=None):
	global log_queue
	global send_queue
	global EXIT_FLAG
	print("\033[0m\033[1;36m再见！\033[0m")
	if side == "Server":
		log_queue.put(json.dumps({'type': 'SERVER.STOP.LOG', 'time': time_str()}))
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({'to': i, 'content': {'type': 'SERVER.STOP.ANNOUNCE'}}))
		time.sleep(1)
	EXIT_FLAG = True
	exit()

def do_help(arg=None):
	print()
	printf(HELP_HINT_1, "cyan")
	print()
	printf(HELP_HINT_2, "blue")
	print()
	printf(HELP_HINT_3, "cyan")
	print()





# ============================= 第四部分：与线程对应的函数 =============================





def thread_gate():
    global online_count
    global log_queue
    global send_queue
    global users
    while True:
        time.sleep(0.1)
        if EXIT_FLAG:
            exit()
            break

        conntmp, addresstmp = None, None
        try:
            conntmp, addresstmp = s.accept()
            conntmp.setblocking(False)
            conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
            conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        except:
            continue

        time.sleep(2)
        data = ""
        while True:
            try:
                data += conntmp.recv(65536).decode('utf-8')
            except:
                break

        tagged = False
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']:
            if method in data:
                try:
                    conntmp.send(bytes(WEBPAGE_CONTENT, encoding="utf-8"))
                    conntmp.close()
                except:
                    pass
                tagged = True
                log_queue.put(json.dumps({'type': 'GATE.INCORRECT_PROTOCOL', 'time': time_str(), 'ip': addresstmp}))
                break
        if tagged:
            continue

        try:
            data = json.loads(data)
            if not isinstance(data, dict) or set(data.keys()) != {"type", "username"} or data['type'] != "GATE.REQUEST" or not isinstance(data['username'], str) or not data['username']:
                raise
        except:
            log_queue.put(json.dumps({'type': 'GATE.INCORRECT_PROTOCOL', 'time': time_str(), 'ip': addresstmp}))
            conntmp.close()
            continue

        # 1. 先检查是否有重复的在线用户
        duplicate_online = False
        for user in users:
            if user['status'] in ["Online", "Admin", "Root"] and user['username'] == data['username']:
                duplicate_online = True
                break
        
        if duplicate_online:
            # 拒绝连接
            result = "Duplicate usernames"
            conntmp.send(bytes(json.dumps({'type': 'GATE.RESPONSE', 'result': result}) + "\n", encoding="utf-8"))
            log_queue.put(json.dumps({'type': 'GATE.CLIENT_REQUEST.LOG', 'time': time_str(), 'ip': addresstmp, 'username': data['username'], 'uid': -1, 'result': result}))
            conntmp.close()
            continue

        # 2. 检查是否有 Offline 的同名用户，如果有则复用其 UID
        existing_uid = None
        for i, user in enumerate(users):
            if user['status'] == "Offline" and user['username'] == data['username']:
                existing_uid = i
                break
        
        if existing_uid is not None:
            # 复用现有用户的 UID
            uid = existing_uid
            users[uid]['body'] = conntmp
            users[uid]['ip'] = addresstmp
            users[uid]['buffer'] = ""
            users[uid]['busy'] = False
            users[uid]['status'] = "Pending"
        else:
            # 创建新用户
            uid = len(users)
            users.append({"body": conntmp, "buffer": "", "ip": addresstmp, "username": data['username'], "status": "Pending", 'busy': False})

        result = "Accepted"
        if config['gate']['enter_check']:
            result = "Pending review"
        if users[uid]['ip'][0] in config['ban']['ip']:
            result = "IP is banned"
        if online_count == config['general']['max_connections']:
            result = "Room is full"
        for word in config['ban']['words']:
            if word in users[uid]['username']:
                result = "Username consists of banned words"

        users[uid]['body'].send(bytes(json.dumps({'type': 'GATE.RESPONSE', 'result': result}) + "\n", encoding="utf-8"))
        log_queue.put(json.dumps({'type': 'GATE.CLIENT_REQUEST.LOG', 'time': time_str(), 'ip': users[uid]['ip'], 'username': users[uid]['username'], 'uid': uid, 'result': result}))
        for i in range(len(users)):
            if users[i]['status'] in ["Online", "Admin", "Root"]:
                send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.CLIENT_REQUEST.ANNOUNCE', 'username': users[uid]['username'], 'uid': uid, 'result': result}}))

        if not result in ["Accepted", "Pending review"]:
            users[uid]['status'] = "Rejected"
            users[uid]['body'].close()
            continue
        if platform.system() != "Windows":
            users[uid]['body'].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            users[uid]['body'].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10800)
            users[uid]['body'].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        else:
            users[uid]['body'].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            users[uid]['body'].ioctl(socket.SIO_KEEPALIVE_VALS, (1, 180000, 30000))
        online_count += 1

        if result == "Accepted":
            users[uid]['status'] = "Online"
            users_abstract = []
            for i in range(len(users)):
                users_abstract.append({"username": users[i]['username'], "status": users[i]['status']})
            users[uid]['body'].send(bytes(json.dumps({'type': 'SERVER.DATA', 'server_version': VERSION, 'uid': uid, 'config': config, 'users': users_abstract, 'chat_history': history}) + "\n", encoding="utf-8"))


def thread_process():
	global online_count
	global receive_queue
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(0.1)
		if EXIT_FLAG:
			exit()
			break
		while not receive_queue.empty():
			message = json.loads(receive_queue.get())
			sender, content = message['from'], message['content']
			if content['type'] == "CHAT.SEND":
				if not content['filename']:
					if content['to'] == -2:
						do_broadcast(None, content['content'], False, sender)
					if content['to'] == -1:
						do_send(None, content['content'], False, sender)
					if content['to'] >= 0:
						do_whisper(str(content['to']), content['content'], False, sender)
				else:
					if content['to'] == -1:
						do_distribute(content['filename'], content['content'], False, sender)
					else:
						do_transfer(str(content['to']) + ' ' + content['filename'], content['content'], False, sender)
			if content['type'] == "GATE.STATUS_CHANGE.REQUEST":
				if content['status'] == "Kicked":
					do_kick(str(content['uid']), False, sender)
				if content['status'] == "Rejected":
					do_doorman("reject " + str(content['uid']), False, sender)
				if content['status'] == "Online":
					do_doorman("accept " + str(content['uid']), False, sender)
			if content['type'] == "SERVER.CONFIG.POST":
				do_config([content['key'], repr(content['value'])], False, sender)

def thread_receive():
	global receive_queue
	global users
	while True:
		time.sleep(0.1)
		if EXIT_FLAG:
			exit()
			break
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"]:
				data = ""
				while True:
					try:
						users[i]['body'].setblocking(False)
						data += users[i]['body'].recv(65536).decode('utf-8')
					except:
						break
				users[i]['buffer'] += data
				while '\n' in users[i]['buffer']:
					try:
						message, users[i]['buffer'] = users[i]['buffer'].split('\n', 1)
					except:
						message, users[i]['buffer'] = users[i]['buffer'], ""
					try:
						message = json.loads(message)
						if not message['type']:
							raise
					except:
						continue
					receive_queue.put(json.dumps({'from': i, 'content': message}))

def thread_send():
	global online_count
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(0.1)
		if EXIT_FLAG:
			exit()
			break
		while not send_queue.empty():
			message = json.loads(send_queue.get())
			if not users[message['to']]['status'] in ["Online", "Admin", "Root"]:
				continue
			try:
				users[message['to']]['body'].send(bytes("\n", encoding="utf-8"))
			except:
				users[message['to']]['status'] = "Offline"
				online_count -= 1
				log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Offline', 'uid': message['to'], 'operator': 0}))
				for i in range(len(users)):
					if users[i]['status'] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({'to': i, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Offline', 'uid': message['to'], 'operator': 0}}))
			try:
				if not message['content']['filename']:
					impossible_value = message['content']['impossible_key']
				with open(message['content']['content'], 'rb') as f:
					file_data = f.read()
				message['content']['content'] = base64.b64encode(file_data).decode('utf-8')
				token = json.dumps(message['content']) + "\n"
				chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
				users[message['to']]['busy'] = True
				time.sleep(0.1)
				for chunk in chunks:
					while True:
						try:
							users[message['to']]['body'].send(bytes(chunk, encoding="utf-8"))
							break
						except BlockingIOError:
							continue
						except:
							break
				time.sleep(0.1)
				users[message['to']]['busy'] = False
			except KeyError:
				users[message['to']]['busy'] = False
				try:
					users[message['to']]['body'].send(bytes(json.dumps(message['content']) + "\n", encoding="utf-8"))
				except:
					pass

def thread_log():
	global log_queue
	while True:
		time.sleep(1)
		if not log_queue.empty():
			with open("./log.txt", "a", encoding="utf-8") as file:
				while not log_queue.empty():
					file.write(log_queue.get() + "\n")
		if EXIT_FLAG:
			exit()
			break

def thread_check():
	global online_count
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(1)
		if EXIT_FLAG:
			exit()
			break
		down = []
		for i in range(len(users)):
			if users[i]['status'] in ["Online", "Admin", "Root"] and not users[i]['busy']:
				try:
					users[i]['body'].send(bytes("\n", encoding="utf-8"))
				except:
					users[i]['status'] = "Offline"
					down.append(i)
					online_count -= 1
					log_queue.put(json.dumps({'type': 'GATE.STATUS_CHANGE.LOG', 'time': time_str(), 'status': 'Offline', 'uid': i, 'operator': 0}))
		for i in down:
			for j in range(len(users)):
				if users[j]['status'] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({'to': j, 'content': {'type': 'GATE.STATUS_CHANGE.ANNOUNCE', 'status': 'Offline', 'uid': i, 'operator': 0}}))

def thread_input():
	global blocked
	global EXIT_FLAG
	while True:
		time.sleep(0.1)
		if EXIT_FLAG:
			exit()
			break
		try:
			input()
		except:
			pass
		blocked = True
		command = input("\033[0m\033[1;30m> ")
		if not command:
			print("\033[8;30m", end="")
			blocked = False
			continue
		command = command.split(' ', 1)
		if len(command) == 1:
			command = [command[0], ""]
		if not command[0] in ['admin', 'ban', 'broadcast', 'config', 'dashboard', 'distribute', 'doorman', 'exit', 'help', 'kick', 'save', 'send', 'transfer', 'whisper']:
			print("指令输入错误。\n\033[8;30m", end="")
			blocked = False
			continue
		now = eval("do_{}".format(command[0]))
		now(command[1])
		print("\033[8;30m", end="")
		blocked = False

def thread_output():
	global EXIT_FLAG
	while True:
		time.sleep(0.1)
		if EXIT_FLAG:
			exit()
			break
		read()
		message = get_message()
		flush()
		if not message:
			continue
		process(message)





# ================================== 第五部分：主程序 ==================================





def main():
	global config
	global blocked
	global my_username
	global my_uid
	global file_order
	global my_socket
	global users
	global s
	global side
	global server_version
	global log_queue
	global receive_queue
	global send_queue
	global print_queue
	global history
	global online_count
	global first_data
	global buffer
	global EXIT_FLAG
	
	try:
		with open("config.json", "r", encoding="utf-8") as f:
			tmp_config = json.load(f)
			if not tmp_config['side'] in ["Server", "Client"]:
				raise
			if tmp_config['side'] == "Server":
				for item, type in CONFIG_TYPE_CHECK_TABLE.items():
					first, second = item.split('.')
					tmp_object = tmp_config[first][second]
					if not eval("isinstance(tmp_object, {})".format(type)):
						raise
					if type == "int" and tmp_object < 1:
						raise
					if item == "message.max_length" and tmp_object > 16384:
						raise
					if item == "file.max_size" and tmp_object > 1073741824:
						raise
					if type == "list":
						for element in tmp_object:
							if not isinstance(element, str):
								raise
						if len(tmp_object) != len(set(tmp_object)):
							raise
					if item == "ban.words":
						for element in tmp_object:
							if '\n' in element or '\r' in element or not element:
								raise
					if item == "ban.ip":
						for element in tmp_object:
							if not check_ip(element):
								raise
					if item == "general.server_ip" and not check_ip(tmp_object):
						raise
					if item == "general.server_port" and tmp_object > 65535:
						raise
					if item == "general.server_username" and not tmp_object:
						raise
					if item == "general.max_connections" and tmp_object > 128:
						raise
				config = tmp_config
			if tmp_config['side'] == "Client":
				if not isinstance(tmp_config['ip'], str):
					raise
				if not isinstance(tmp_config['port'], int):
					raise
				if not isinstance(tmp_config['username'], str):
					raise
				if int(tmp_config['port']) > 65535:
					raise
				if not tmp_config['username']:
					raise
				if not check_ip(tmp_config['ip']):
					raise
				config = tmp_config
	except:
		config = DEFAULT_SERVER_CONFIG
	
	clear_screen()
	prints("欢迎使用 TouchFish 聊天室！", "yellow")
	prints("当前程序版本：{}".format(VERSION), "yellow")
	prints("5 秒后将会自动按上次的配置启动。", "yellow")
	prints("按下 Ctrl + C 以指定启动配置。", "yellow")
	auto_start = True
	try:
		for i in range(5, 0, -1):
			prints("剩余 "+str(i)+" 秒...", "yellow")
			time.sleep(1)
	except KeyboardInterrupt:
		auto_start = False
	except:
		pass
	tmp_side = None
	if not auto_start:
		tmp_side = input("\033[0m\033[1;37m启动类型 (Server = 服务端, Client = 客户端) [{}]：".format(config['side']))
	if not tmp_side:
		tmp_side = config['side']
	if not tmp_side in ["Server", "Client"]:
		prints("参数错误。", "red")
		input("\033[0m")
		sys.exit(1)
	
	if tmp_side == "Server":
		if config['side'] == "Client":
			config = DEFAULT_SERVER_CONFIG
		tmp_ip = None
		if not auto_start:
			tmp_ip = input("\033[0m\033[1;37m服务器 IP [{}]：".format(config['general']['server_ip']))
		if not tmp_ip:
			tmp_ip = config['general']['server_ip']
		config['general']['server_ip'] = tmp_ip
		if not check_ip(tmp_ip):
			prints("参数错误：输入的服务器 IP 不是有效的点分十进制格式 IPv4 地址。", "red")
			input("\033[0m")
			sys.exit(1)
		tmp_port = None
		if not auto_start:
			tmp_port = input("\033[0m\033[1;37m端口 [{}]：".format(config['general']['server_port']))
		if not tmp_port:
		   tmp_port = config['general']['server_port']
		try:
			tmp_port = int(tmp_port)
			if tmp_port < 1 or tmp_port > 65535:
				raise
		except:
			prints("参数错误：端口号应为不大于 65535 的正整数。", "red")
			input("\033[0m")
			sys.exit(1)
		config['general']['server_port'] = tmp_port
		tmp_server_username = None
		if not auto_start:
			tmp_server_username = input("\033[0m\033[1;37m服务器管理员的用户名 [{}]：".format(config['general']['server_username']))
		if not tmp_server_username:
		   tmp_server_username = config['general']['server_username']
		config['general']['server_username'] = tmp_server_username
		my_username = config['general']['server_username']
		tmp_max_connections = None
		if not auto_start:
			tmp_max_connections = input("\033[0m\033[1;37m最大在线连接数 [{}]：".format(config['general']['max_connections']))
		if not tmp_max_connections:
		   tmp_max_connections = config['general']['max_connections']
		try:
			tmp_max_connections = int(tmp_max_connections)
			if tmp_max_connections < 1 or tmp_max_connections > 128:
				raise
		except:
			prints("参数错误：最大在线连接数应为不大于 128 的正整数。", "red")
			input("\033[0m")
			sys.exit(1)
		config['general']['max_connections'] = tmp_max_connections
		
		os.system('mkdir TouchFishFiles')
		try:
			with open("config.json", "w", encoding="utf-8") as f:
				json.dump(config, f)
			prints("本次连接中输入的参数已经保存到配置文件 config.json，下次连接时将自动加载。", "yellow")
		except:
			prints("启动时遇到错误：配置文件 config.json 写入失败。", "red")
			input("\033[0m")
			sys.exit(1)
		try:
			with open("log.txt", "a", encoding="utf-8") as f:
				pass
		except:
			prints("启动时遇到错误：无法向日志文件 log.txt 写入内容。", "red")
			input("\033[0m")
			sys.exit(1)
		
		try:
			s = socket.socket()
			s.bind((config['general']['server_ip'], config['general']['server_port']))
			s.listen(config['general']['max_connections'])
			s.setblocking(False)
			users = [{"body": None, "extra": None, "buffer": "", "ip": None, "username": config['general']['server_username'], "status": "Root", "busy": False}]
			root_socket = socket.socket()
			root_socket.connect((config['general']['server_ip'], config['general']['server_port']))
			root_socket.setblocking(False)
			root_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
			root_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
			users[0]['body'], users[0]['ip'] = s.accept()
			users[0]['body'].setblocking(False)
			users[0]['body'].setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
			users[0]['body'].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
			my_socket = root_socket
		except:
			prints("启动时遇到错误：无法在给定的地址上启动 socket，请检查 IP 地址或更换端口。", "red")
			input("\033[0m")
			sys.exit(1)
		
		with open("./log.txt", "a", encoding="utf-8") as file:
			file.write(json.dumps({'type': 'SERVER.START', 'time': time_str(), 'server_version': VERSION, 'config': config}) + "\n")
		
		side = "Server"
		prints("启动成功！", "green")
		ring()
		do_help()
		do_dashboard()
		if config['gate']['enter_hint']:
			first_line = dye("[" + str(datetime.datetime.now())[11:19] + "]", "black")
			first_line += dye(" [您发送的]", "blue")
			first_line += " "
			first_line += dye(" [加入提示]", "red")
			first_line += " "
			first_line += dye("@", "black")
			first_line += dye(config['general']['server_username'], "yellow")
			first_line += dye(":", "black")
			prints(first_line)
			prints(config['gate']['enter_hint'], "white")
		
		THREAD_GATE = threading.Thread(target=thread_gate)
		THREAD_PROCESS = threading.Thread(target=thread_process)
		THREAD_RECEIVE = threading.Thread(target=thread_receive)
		THREAD_SEND = threading.Thread(target=thread_send)
		THREAD_LOG = threading.Thread(target=thread_log)
		THREAD_CHECK = threading.Thread(target=thread_check)
		THREAD_INPUT = threading.Thread(target=thread_input)
		THREAD_OUTPUT = threading.Thread(target=thread_output)
		
		THREAD_GATE.start()
		THREAD_PROCESS.start()
		THREAD_RECEIVE.start()
		THREAD_SEND.start()
		THREAD_LOG.start()
		THREAD_CHECK.start()
		THREAD_INPUT.start()
		THREAD_OUTPUT.start()
	
	if tmp_side == "Client":
		if config['side'] == "Server":
			config = DEFAULT_CLIENT_CONFIG
		tmp_ip = None
		if not auto_start:
			tmp_ip = input("\033[0m\033[1;37m服务器 IP [{}]：".format(config['ip']))
		if not tmp_ip:
			tmp_ip = config['ip']
		config['ip'] = tmp_ip
		if not check_ip(tmp_ip):
			prints("参数错误：输入的服务器 IP 不是有效的点分十进制格式 IPv4 地址。", "red")
			input("\033[0m")
			sys.exit(1)
		tmp_port = None
		if not auto_start:
			tmp_port = input("\033[0m\033[1;37m端口 [{}]：".format(config['port']))
		if not tmp_port:
		   tmp_port = config['port']
		try:
			tmp_port = int(tmp_port)
			if tmp_port < 1 or tmp_port > 65535:
				raise
		except:
			prints("参数错误：端口号应为不大于 65535 的正整数。", "red")
			input("\033[0m")
			sys.exit(1)
		config['port'] = tmp_port
		tmp_username = None
		if not auto_start:
			tmp_username = input("\033[0m\033[1;37m用户名 [{}]：".format(config['username']))
		if not tmp_username:
		   tmp_username = config['username']
		config['username'] = tmp_username
		my_username = config['username']
		
		os.system('mkdir TouchFishFiles')
		try:
			with open("config.json", "w", encoding="utf-8") as f:
				json.dump(config, f)
			prints("本次连接中输入的参数已经保存到配置文件 config.json，下次连接时将自动加载。", "yellow")
		except:
			prints("启动时遇到错误：配置文件 config.json 写入失败。", "red")
			input("\033[0m")
			sys.exit(1)
		
		prints("正在连接聊天室...", "yellow")
		my_socket = socket.socket()
		try:
			my_socket.connect((config['ip'], config['port']))
			my_socket.setblocking(False)
			my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
			my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
			my_socket.send(bytes(json.dumps({'type': 'GATE.REQUEST', 'username': my_username}), encoding="utf-8"))
			time.sleep(3)
		except Exception as e:
			prints("连接失败：{}".format(e), "red")
			input("\033[0m")
			sys.exit(1)
		
		if platform.system() == "Windows":
			my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
			my_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 180000, 30000))
		else:
			my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
			my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10800)
			my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
		
		try:
			read()
			message = get_message()
			if not message['result'] in ["Accepted", "Pending review", "IP is banned", "Room is full", "Duplicate usernames", "Username consists of banned words"]:
				raise
		except:
			prints("连接失败：对方似乎不是 v4 及以上的 TouchFish 服务端。", "red")
			input("\033[0m")
			sys.exit(1)
		
		if not message['result'] in ["Accepted", "Pending review"]:
			prints("连接失败：{}".format(RESULTS[message['result']]), "red")
			input("\033[0m")
			sys.exit(1)
		
		if message['result'] == "Accepted":
			prints("连接成功！", "green")
			ring()
		
		if message['result'] == "Pending review":
			prints("服务端需要对连接请求进行人工审核，请等待...", "white")
			while True:
				try:
					read()
					message = get_message()
					if not message:
						continue
					if not message['accepted']:
						prints("服务端管理员 {} (UID = {}) 拒绝了您的连接请求。".format(message['operator']['username'], message['operator']['uid']), "red")
						prints("连接失败。", "red")
						input("\033[0m")
						sys.exit(1)
					if message['accepted']:
						time.sleep(3)
						prints("服务端管理员 {} (UID = {}) 通过了您的连接请求。".format(message['operator']['username'], message['operator']['uid']), "green")
						prints("连接成功！", "green")
						ring()
						break
				except:
					pass
		
		side = "Client"
		read()
		first_data = get_message()
		server_version = first_data['server_version']
		my_uid = first_data['uid']
		config = first_data['config']
		users = first_data['users']
		online_count = 0
		for user in users:
			if user['status'] in ["Online", "Admin", "Root"]:
				online_count += 1
		do_help()
		do_dashboard()
		for i in first_data['chat_history']:
			print_message(i)
		if config['gate']['enter_hint']:
			first_line = dye("[" + str(datetime.datetime.now())[11:19] + "]", "black")
			first_line += dye(" [加入提示]", "red")
			first_line += " "
			first_line += dye("@", "black")
			first_line += dye(config['general']['server_username'], "yellow")
			first_line += dye(":", "black")
			prints(first_line)
			prints(config['gate']['enter_hint'], "white")
		
		THREAD_INPUT = threading.Thread(target=thread_input)
		THREAD_OUTPUT = threading.Thread(target=thread_output)
		
		THREAD_INPUT.start()
		THREAD_OUTPUT.start()

if __name__ == "__main__":
	main()





# End of program
