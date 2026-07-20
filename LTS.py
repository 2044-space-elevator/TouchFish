#!/usr/bin/env python3





# TouchFish LTS Client/Server Unified Program (Security Updates, Version 4)





"""
# TouchFish 协议文档

本协议文档版本：v2.8.0

本协议分为三个部分：`Gate`，`Chat`，`Server`。

协议均使用 NDJSON（JSON 格式，相邻两个 JSON 以换行符分隔）格式进行发送。

---

# 协议更新日志

- Protocol v2.8.0 (TouchFish v4.11.0)
  - 撤销 v2.3.0 的字段更改
- Protocol v2.7.0 (TouchFish v4.10.0)
  - 添加对心跳数据的说明，没有实际改动
- Protocol v2.6.0 (TouchFish v4.9.0)
  - 恢复 v2.3.0 的字段更改
- Protocol v2.5.0 (TouchFish v4.8.0)
  - 撤销 v2.3.0 的字段更改
- Protocol v2.4.0 (TouchFish v4.7.0)
  - 在 MISC.START 添加 stamp 字段
- Protocol v2.3.0 (TouchFish v4.6.0)
  - 将 SERVER 部分整体更名为 MISC 部分
  - 将 SERVER.STOP 部分整体更名为 MISC.SERVER_STOP 部分
  - 将 MISC.START 部分的 server_version 字段更名为 version 字段
  - 增加 MISC.COMMAND 和 MISC.CLIENT_STOP 协议
- Protocol v2.2.0 (TouchFish v4.4.0)
  - 更改 CHAT.RECEIVE 和 CHAT.LOG 协议中 order 的定义
- Protocol v2.1.0 (TouchFish v4.1.0)
  - 将 SERVER.STOP 更名为 SERVER.STOP.LOG
  - 增加 SERVER.STOP.ANNOUNCE 协议
- Protocol v2.0.0 (TouchFish v4.0.0)
  - 完整重构了协议

由于 v2 完整重构了协议，v1 部分的协议更新日志不再列出。

---

# 1 Gate

这个部分是关于进入聊天室的请求、审核等操作的协议内容。

## 1.1 Request

`{ type: "GATE.REQUEST", username: string }`

客户端连接时向服务端发送此消息，用于申请加入。

- `type`: `"GATE.REQUEST"`（所有协议的 `type` 字段均为固定值，下同）
- `username`: 字符串，表示用户希望使用的用户名。（所有 `username` 字段必须非空，下同）

## 1.2 Response

`{ type: "GATE.RESPONSE", result: "Accepted" | "Pending review" | "IP is banned" | "Room is full" | "Duplicate usernames" | "Username consists of banned words" }`

服务端对 `1.1 Request` 的直接响应，告知客户端其请求的处理结果。

- `type`: `"GATE.RESPONSE"`
- `result`: 字符串，可能取值包括：（下同）
  - `"Accepted"`：立即允许加入。
  - `"Pending review"`：需人工审核。
  - `"IP is banned"`：当前 IP 被封禁。
  - `"Room is full"`：服务端用户数已达上限。
  - `"Duplicate usernames"`：用户名已被使用。
  - `"Username consists of banned words"`：用户名包含违禁词。

## 1.3 Review Result

`{ type: "GATE.REVIEW_RESULT", accepted: boolean, operator: { username: string, uid: number } }`

当请求状态为 `"Pending review"` 时，管理员审核完成后，服务端向该客户端发送此消息。

- `type`: `"GATE.REVIEW_RESULT"`
- `accepted`: 布尔值，`true` 表示通过，`false` 表示拒绝。
- `operator`: 审核者信息：
  - `username`: 操作者用户名。
  - `uid`: 操作者的用户 ID。（除特殊说明外，用户 ID 为非负整数，下同）

## 1.4 Incorrect Protocol

`{ type: "GATE.INCORRECT_PROTOCOL", time: time, ip: ip }`

当出现通信不符合协议规范的连接时，服务端向日志写入记录。

- `type`: `"GATE.INCORRECT_PROTOCOL"`
- `time`: 表示事件发生的时间。（精确到微秒，下同）
- `ip`: 字符串，表示连接的网络地址。（格式为 `IPv4:port`，下同）

## 1.5 Client Request

服务端对客户端连接请求的响应。

### 1.5.1 Announce

`{ type: "GATE.CLIENT_REQUEST.ANNOUNCE", username: string, uid: number, result: "Accepted" | "Pending review" | "IP is banned" | "Room is full" | "Duplicate usernames" | "Username consists of banned words" }`

服务端向所有已连接的客户端广播该客户端的连接请求。

- `type`: `"GATE.CLIENT_REQUEST.ANNOUNCE"`
- `username`: 用户名。
- `uid`: 服务端为该用户分配的用户 ID。
- `result`: 服务端对该请求的处理结果。

### 1.5.2 Log

`{ type: "GATE.CLIENT_REQUEST.LOG", time: time, ip: ip, username: string, uid: number }`

服务端向接收到的连接请求写入日志。

- `type`: `"GATE.CLIENT_REQUEST.LOG"`
- `time`: 同上。
- `ip`: 客户端 IP 地址与端口。
- `username`: 用户名。
- `uid`: 用户 ID。

## 1.6 Status Change

关于用户状态变更事件的协议。

### 1.6.1 Request

`{ type: "GATE.STATUS_CHANGE.REQUEST", status: "Rejected" | "Kicked" | "Offline" | "Pending" | "Online" | "Admin" | "Root", uid: number }`

由管理员向服务端发起的用户状态变更请求。

- `type`: `"GATE.STATUS_CHANGE.REQUEST"`
- `status`: 字符串，表示目标状态，可能取值包括：（下同）
  - `"Rejected"`：连接被拒绝的用户。（本协议中表示管理员拒绝加入请求）
  - `"Kicked"`：被踢出聊天室的用户。（本协议中表示管理员主动踢出用户）
  - `"Offline"`：主动离开聊天室的用户。（本协议中不会出现）
  - `"Pending"`：等待加入审核的用户。（本协议中不会出现）
  - `"Online"`：在线用户。（本协议中表示管理员通过加入请求）
  - `"Admin"`：在线管理员。（本协议中不会出现）
  - `"Root"`：聊天室房主。（本协议中不会出现）
- `uid`: 被操作用户的用户 ID。

### 1.6.2 Announce

`{ type: "GATE.STATUS_CHANGE.ANNOUNCE", status: "Rejected" | "Kicked" | "Offline" | "Pending" | "Online" | "Admin" | "Root", uid: number }`

当用户状态变更时，服务端进行广播。

- `type`: `"GATE.STATUS_CHANGE.ANNOUNCE"`
- `status`: 新状态。
- `uid`: 被变更状态的用户 ID。

### 1.6.3 Log

`{ type: "GATE.STATUS_CHANGE.LOG", time: time, status: "Rejected" | "Kicked" | "Offline" | "Pending" | "Online" | "Admin" | "Root", uid: number, operator: number }`

服务端将用户状态变更事件写入日志。

- `type`: 固定为 `"GATE.STATUS_CHANGE.LOG"`。
- `time`: 同上。
- `status`: 新状态。（`Pending` 状态和 `Root` 状态不会出现）
- `uid`: 被操作用户的用户 ID。
- `operator`: 操作者的用户 ID。

---

# 2 Chat

这个部分是关于在聊天室内收发消息和文件的协议内容。

## 2.1 Send

`{ type: "CHAT.SEND", filename: string, content: string, to: number | -1 | -2 }`

客户端发送消息或文件。

- `type`: `"CHAT.SEND"`
- `filename`: 若发送的是普通文本消息，则为空字符串 `""`；若发送文件，则为原始文件名。（下同）
- `content`: 若为消息，则为原始文本内容；若为文件，则为文件内容的 Base64 编码字符串。（下同）
- `to`: 目标接收者，可能取值包括：（下同）
  - `-2`：广播给所有在线用户（相较于普通发送有特殊提示）。
  - `-1`：发送给所有在线用户。
  - 非负整数：私聊给拥有相应用户 ID 的用户。

## 2.2 Receive

`{ type: "CHAT.RECEIVE", from: number, order: signed number, filename: string, content: string, to: number | -1 | -2 }`

服务端将消息转发给目标客户端。

- `type`: `"CHAT.RECEIVE"`
- `from`: 发送者的用户 ID。（下同）
- `order`: 消息编号，可能取值包括：（下同）
  - 正整数：普通文本消息。
  - 负整数：文件编号。
- `filename`: 同上。
- `content`: 同上。
- `to`: 同上。

## 2.3 Log

`{ type: "CHAT.LOG", time: time, from: number, order: signed number, filename: string, content: string, to: number | -1 | -2 }`

服务端将收到的聊天记录写入日志。

- `type`: `"CHAT.LOG"`
- `time`: 同上。
- `from`: 同上。
- `order`: 同上。
- `filename`: 同上。
- `content`: 若为消息，则为原始文本内容；若为文件，则为空字符串 `""`。（为了防止日志文件过大，具体的文件内容会单独存储）
- `to`: 同上。

---

# 3 Server

这个部分是关于程序运行情况的协议内容。

## 3.1 Start

`{ type: "SERVER.START", time: time, stamp: number, version: string, config: JSON }`

程序将启动时的启动参数写入日志。

- `type`: `"SERVER.START"`
- `time`: 同上。
- `stamp`: 用于指定文件保存路径，取启动时的 UNIX 时间戳乘 `10 ** 6` 后向下取整。
- `version`: 字符串，表示服务端程序版本。（下同）
- `config`: JSON 对象，表示启动参数。（具体格式详见代码，下同）

## 3.2 Data

`{ type: "SERVER.DATA", server_version: string, uid: number, config: JSON, users: [JSON, ...], chat_history: [JSON, ...] }`

用于向新连接的客户端提供完整上下文。

- `type`: `"SERVER.DATA"`
- `server_version`: 同上。
- `uid`: 表示服务端分配给该用户的用户 ID。
- `config`: 同上。
- `users`: 用户列表，每个元素为：
  - `username`: 用户名。
  - `status`: 同上。
- `chat_history`: 历史聊天记录，每条记录包含：（不包含私聊记录和文件发送记录）
  - `time`: 同上。
  - `order`：同上。
  - `from`: 同上。
  - `content`: 同上。
  - `to`: 同上。

## 3.3 Command

`{ type: "SERVER.COMMAND", time: time, command: string }`

程序将用户输入的指令写入日志。

- `type`: `"SERVER.COMMAND"`
- `time`: 同上。
- `command`: 输入的指令。

## 3.4 Stop

程序正常关闭时的协议。

### 3.4.1 Announce

`{ type: "SERVER.STOP.ANNOUNCE" }`

服务端正常关闭时，向全体客户端进行广播。

- `type`: `"SERVER.STOP.ANNOUNCE"`

### 3.4.2 Log

`{ type: "SERVER.STOP.LOG", time: time }`

程序正常关闭时将事件写入日志。

- `type`: `"SERVER.STOP.LOG"`
- `time`: 同上。

## 3.5 Config

### 3.5.1 Post

`{ type: "SERVER.CONFIG.POST", key: string, value: any }`

管理员向服务端发送配置修改请求。

- `type`: `"SERVER.CONFIG.POST"`
- `key`: 配置项名称。（下同）
- `value`: 配置值。（下同）

### 3.5.2 Change

`{ type: "SERVER.CONFIG.CHANGE", key: string, value: any, operator: number }`

服务端向客户端广播配置修改事件。

- `type`: `"SERVER.CONFIG.CHANGE"`
- `key`: 同上。
- `value`: 同上。
- `operator`: 执行修改操作的用户 ID。

### 3.5.3 Save

`{ type: "SERVER.CONFIG.SAVE", time: time }`

服务端将聊天室房主导出配置的事件写入日志。

- `type`: `"SERVER.CONFIG.SAVE"`
- `time`: 同上。

### 3.5.4 Log

`{ type: "SERVER.CONFIG.LOG", time: time, key: string, value: any, operator: number }`

服务端将配置修改事件写入日志。

- `type`: `"SERVER.CONFIG.LOG"`
- `time`: 同上。
- `key`: 同上。
- `value`: 同上。
- `operator`: 执行修改操作的用户 ID。

# 4 Keepalive

发送的消息中可能包含空行，这些空行起心跳数据的作用。
"""





# ============================== 第一部分：常量和变量定义 ==============================





# 所有的模块依赖
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

# 程序版本
VERSION = "v4.11.0"

# 用于客户端解析协议 1.2
RESULTS = \
{
	"IP is banned": "您的 IP 被服务端封禁。",
	"Room is full": "服务端连接数已满，无法加入。",
	"Duplicate usernames": "该用户名已被占用，请更换用户名。",
	"Username consists of banned words": "用户名中包含违禁词，请更换用户名。"
}

# 用于输出 ANSI 颜色转义字符 \033[1;3*m，具体如下：
"""
灰色 (black):
- 输入模式中的所有输入输出文本（除了 help 指令的输出）
- 消息头中用户名前的 @ 符号，行末的 : 符号，以及时间戳
- 启动成功时输出的聊天室信息（本质为模拟 dashboard 指令调用）
红色 (red):
- [加入提示]，[公告]，[广播]，[文件] 标签的颜色
- 启动阶段的失败提示
绿色 (green):
- [私聊] 标签的颜色
- 私聊消息的消息头中中发送方和接收方之间的 -> 连接符
- 启动阶段的成功提示
蓝色 (blue):
- [发给您的]，[您发送的] 标签的颜色
- help 指令显示的帮助消息中的第三段和第六段
白色 (white):
- 普通消息和加入提示的文本
- 启动阶段的参数输入提示
- 启动阶段中创建 TouchFishFiles 目录（客户端用于存放
  接收到的文件，服务端用于存放所有经服务端传输的文件）
  失败（例如，目录已经存在）时的系统提示
黄色 (yellow):
- 消息头中的用户名
- 启动阶段中上面没有提到的所有文本
青色 (cyan):
- 所有除普通消息和加入提示以外的消息的文本
- help 指令显示的帮助消息中的其余段落
- 程序关闭时的「再见！」文本

特别说明：
- shell 指令的输出文本颜色为系统默认颜色
- 洋红色 (magenta) 目前没有使用过
"""
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

# 默认客户端配置（必须在启动时指定）：
"""
side            角色 (Client)
ip              服务端地址
port            服务端端口
username        连接时使用的用户名
"""
# 需要指出的是，第五部分中会给 username 字段
# 的默认值后面加上一个随机六位数作为后缀，
# 形成形如 "user123456" 的用户名
DEFAULT_CLIENT_CONFIG = {"side": "Client", "ip": "touchfish.xin", "port": 11451, "username": "user"}

# 默认服务端配置（side 和 general.* 必须在启动时指定）：
"""
side                        角色 (Server)
general.server_ip           服务端地址
general.server_port         服务端端口
general.server_username     服务端用户使用的用户名
general.max_connections     最大允许连接数，
                            参见下面对 online_count 变量的说明
...                         其余参数不必在启动时指定，
                            具体内容及含义参见 CONFIG_LIST 常量
"""
DEFAULT_SERVER_CONFIG = \
{
	"side": "Server",
	"general": {"server_ip": "0.0.0.0", "server_port": 8080, "server_username": "root", "max_connections": 128},
	"ban": {"ip": [], "words": []},
	"gate": {"enter_hint": "", "enter_check": False},
	"message": {"allow_private": True, "max_length": 16384},
	"file": {"allow_any": True, "allow_private": True, "max_size": 1048576}
}

# 服务端配置中的期望数据类型，额外限制如下：
"""
side                        必须为 "Server"（此处没有列出）
general.server_ip           必须为合法 IPv4
general.server_port         必须在 [1, 65535] 中取值
general.server_username     不能为空串
general.max_connections     必须在 [1, 128] 中取值
ban.ip                      必须全部为合法 IPv4，不能有重复项
ban.words                   不能为空串，不能包含 \r 或 \n，不能有重复项
message.max_length          必须在 [1, 16384] 中取值
file.max_size               必须在 [1, 1073741824] (1 Byte - 1 GiB) 中取值，
                            实际判定时向下取整到 3 的倍数
"""
# general.server_ip 中给出的 IPv4 可以在 ban.ip 列表中出现，
# 且启动服务端时不会进行相关检查；
# ban.words 的检查范围包括消息文本，所发送的文件的文件名和
# 客户端连接时使用的用户名，但不包含 general.server_port
# 中指定的服务端用户名和所发送的文件的内容；
# message.max_length 参数以「字符 (Unicode 码点) 个数」为准，
# 例如「你好」算作 2 个字符；
# file.max_size 参数以「字节个数」为准，
# 例如 UTF-8 格式的文本「你好」算作 6 个字节
CONFIG_TYPE_CHECK_TABLE = \
{
	"general.server_ip": "str", "general.server_port": "int", "general.server_username": "str", "general.max_connections": "int",
	"ban.ip": "list", "ban.words": "list",
	"gate.enter_hint": "str", "gate.enter_check": "bool",
	"message.allow_private": "bool", "message.max_length": "int",
	"file.allow_any": "bool", "file.allow_private": "bool", "file.max_size": "int"
}

# 客户端配置中的期望数据类型如下，此处没有单独编写代码：
"""
side                        必须为 "Client"
ip                          不能为空串
port                        必须在 [1, 65535] 中取值
username                    不能为空串
"""

# 用于 dashboard 指令中列出参数列表
CONFIG_LIST = \
"""
参数名称                当前值      修改示例        描述

ban.ip                  <1>         ["8.8.8.8"]     IP 黑名单
ban.words               <2>         ["a", "b"]      屏蔽词列表

gate.enter_hint         <3>         "Hi there!\\n"   进入提示
gate.enter_check        {!s:<12}True            加入是否需要人工放行

message.allow_private   {!s:<12}False           是否允许私聊
message.max_length      {:<12}256             最大消息长度（字符个数）

file.allow_any          {!s:<12}False           是否允许发送文件
file.allow_private      {!s:<12}False           是否允许发送私有文件
file.max_size           {:<12}16384           最大文件大小（字节数）

为了防止尖括号处的内容写不下，此处单独列出：
<1>:
{}
<2>:
{}
<3>:
{}
"""[1:-1]

# 指令列表
COMMAND_LIST = ["admin", "ban", "broadcast", "config", "dashboard", "distribute", "doorman", "evaluate", "exit", "flood", "help", "kick", "save", "send", "shell", "transfer", "whisper"]

# 缩写表
ABBREVIATION_TABLE = \
{
	"D": "dashboard", "F": "distribute", "Q": "evaluate", "E": "exit", "L": "flood",
	"H": "help", "S": "send", "J": "shell", "T": "transfer", "P": "whisper",
	"I+": "ban ip add", "I-": "ban ip remove", "W+": "ban words add", "W-": "ban words remove",
	"B": "broadcast", "C": "config", "G+": "doorman accept", "G-": "doorman reject", "K": "kick",
	"A+": "admin add", "A-": "admin remove", "V": "save",
	"d": "dashboard", "f": "distribute", "q": "evaluate", "e": "exit", "l": "flood",
	"h": "help", "s": "send", "j": "shell", "t": "transfer", "p": "whisper",
	"i+": "ban ip add", "i-": "ban ip remove", "w+": "ban words add", "w-": "ban words remove",
	"b": "broadcast", "c": "config", "g+": "doorman accept", "g-": "doorman reject", "k": "kick",
	"a+": "admin add", "a-": "admin remove", "v": "save"
}

# flood 指令开启的简易命令行模式的进入提示
SIMPLE_COMMAND_LINE_HINT_CONTENT = \
"""
您已经进入简易命令行模式。
在简易命令行模式中，您只需要执行以下三个步骤，即可完成单行公开消息的发送：
    1. 按下 Enter 进入输入模式
    2. 直接输入想要发送的单行消息（不需要显式执行 send 指令）
    3. 再按下 Enter 返回输出模式
本模式下发送结果不会进行显式反馈，而是根据下面的特性间接反馈：
发送成功的消息能够在输出模式中看到（带有响铃），发送失败的消息则不会。
在任何模式下按下 Ctrl + {} 以退出简易命令行模式。
"""[1:-1]

# help 指令显示的帮助消息（分为 8 段）
HELP_HINT_CONTENT = \
[
"""
聊天室界面分为输出模式和输入模式，默认为输出模式，此时行首没有符号。
按下回车键即可从输出模式转为输入模式，此时行首有一个 > 符号。
按下 Enter（或输入任意指令）即可从输入模式转换回输出模式。
输出模式下，输入的指令将被忽略，且不会显示在屏幕上。
输入模式下，新的消息将等待到退出输入模式才会显示。
聊天室内可用的指令有：
"""[1:-1],

"""
聊天室内用户的状态分为以下 7 种：
"""[1:-1],

"""
        Root            聊天室房主
        Admin           聊天室管理员
        Online          聊天室普通用户
        Pending         等待加入审核的用户
        Offline         主动离开聊天室的用户
        Kicked          被踢出聊天室的用户
        Rejected        连接被拒绝的用户
""",

"""
有且只有状态为 Root，Admin，Online 和 Pending 的用户会被计入在线用户数。
需要指出的是，状态为 Admin 和 Root 有权查看别人的私聊消息和私有文件。
"""[1:-1],

"""
聊天室内可用的指令分为以下 17 条 25 项：
"""[1:-1],

"""
     [D]    dashboard                    展示聊天室各项数据
     [F]    distribute <filename>        发送文件
     [Q]    evaluate <input>             像 Python IDLE 那样计算输入数据
     [E]    exit                         退出或关闭聊天室
     [L]    flood                        开启简易命令行模式
     [H]    help                         显示本帮助文本
     [S]    send                         发送多行消息
     [S]    send <message>               发送单行消息
     [J]    shell <command>              执行 Shell 指令
     [T]    transfer <user> <filename>   向某个用户发送私有文件
     [P]    whisper <user>               向某个用户发送多行私聊消息
     [P]    whisper <user> <message>     向某个用户发送单行私聊消息
    [I+]  * ban ip add <ip>              封禁 IP 或 IP 段
    [I-]  * ban ip remove <ip>           解除封禁 IP 或 IP 段
    [W+]  * ban words add <word>         屏蔽某个词语
    [W-]  * ban words remove <word>      解除屏蔽某个词语
     [B]  * broadcast                    向全体用户广播多行消息
     [B]  * broadcast <message>          向全体用户广播单行消息
     [C]  * config <key> <value>         修改聊天室配置项
    [G+]  * doorman accept <user>        通过某个用户的加入申请
    [G-]  * doorman reject <user>        拒绝某个用户的加入申请
     [K]  * kick <user>                  踢出某个用户
    [A+] ** admin add <uid>              添加管理员
    [A-] ** admin remove <uid>           移除管理员
     [V] ** save                         保存聊天室配置项信息
""",

"""
缩略表示形式不区分大小写，其他字段区分大小写。
支持用左边方括号内的内容缩略表示右边所有没有用尖括号括起来的字段。
所有 <user> 字段可以输入 UID 或用户名均可，优先解析为 UID。
解析用户名遇到冲突时采纳 UID 最小的合法解析结果。
简易命令行模式允许您直接输入并发送单行消息而省略 send，但会禁用其他指令。
标注 * 的指令只有状态为 Admin 或 Root 的用户可以使用。
标注 ** 的指令只有状态为 Root 的用户可以使用。
对于 dashboard 指令，状态为 Root 的用户可以看到所有用户的 IP 地址，其他用户不能。
对于 evaluate 指令，该指令直接使用 eval() 函数实现，其中二进制发行版的 Python 版本为 3.6。
对于 evaluate 指令，请不要注入恶意代码（典型的有 globals(), locals() 等），否则后果自负。
对于 shell 指令，请不要试图执行危害本程序（或您的设备）的指令（此处从略），否则后果自负。
对于 ban ip 指令，支持输入形如 a.b.c.d/e 的 IP 段，但前缀长度 (e 值) 不得小于 24。
对于 config 指令，<key> 的格式以 dashboard 指令输出的参数名称为准。
对于 config 指令，<value> 的格式以 dashboard 指令输出的修改示例为准。
对于 kick 指令，状态为 Root 的用户可以踢出状态为 Admin 或 Online 的用户。
对于 kick 指令，状态为 Admin 的用户只能踢出状态为 Online 的用户。
对于 kick 指令，状态为 Admin 的用户只能踢出状态为 Online 的用户。
"""[1:-1],

"""
您可以在 TouchFish 的官方 Github 仓库页面获取更多联机帮助：
https://github.com/2044-space-elevator/TouchFish
"""[1:-1]
]

HELP_HINT_COLORS = ["cyan", "cyan", "blue", "cyan", "cyan", "blue", "cyan", "cyan"]

HELP_HINT = [{"content": HELP_HINT_CONTENT[i], "color": HELP_HINT_COLORS[i]} for i in range(len(HELP_HINT_CONTENT))]

# 当服务端收到不遵守 TouchFish v4 协议的连接时，
# 假设其为浏览器访问公共聊天室，显示 HTML 提示页面
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

"""
以下是在服务端和客户端都启用的变量：
config              服务端参数（对于客户端，启动前存储客户端参数，
                    启动后存储服务端参数）
blocked             True 表示 HELP_HINT 第 1 段提到的「输入模式」，
                    False 表示「输出模式」
stamp               自身保存文件时的路径，具体为
                    ./TouchFishFiles/<stamp>/<file_order>.file
                    （<file_order> 取绝对值），取值为启动时的
                    UNIX 时间戳乘上 (10 ** 6) 后向下取整的值
my_username         自身连接的用户名
my_uid              自身的用户 ID（服务端为 0，客户端从 1 开始分配）
my_socket           自身的 TCP socket 连接（服务端也有连接，
                    但 my_socket 一端只读取不发送）
users               用户信息（JSON 格式列表，
                    但服务端和客户端中 JSON 结构不同，详见下文）
side                角色（服务端取 "Server"，客户端取 "Client"）
server_version      服务端版本
online_count        在线人数（包括状态为 Root，Admin，
                    Online 和 Pending 的用户，这些状态的含义
                    参见 HELP_HINT 第 3 段，下同）
buffer              my_socket 读取时模拟的缓冲区
                    （发送的数据都是 NDJSON，因此遇到换行符则清空）
bell_countdown      用于在收到广播时响铃 5 次以体现公告的重要性，
                    第 1 次为默认响铃，后 4 次中每 1.5 秒响铃一次，
                    对应 15 次 thread_output 的循环
exit_flag           默认为 False，程序终止改为 True，通知所有线程终止
log_queue           记录需要写入日志的信息，数据格式为 str(JSON)
print_queue         用于输入模式下记录被阻塞的输出内容（每行一条），
                    切换到输出模式后一并输出

以下是服务端启用而客户端不启用的变量：
file_order          目前服务端已经传送的文件个数，
                    用于从 -1 开始分配文件 ID (-1, -2, -3, ...)，区分文件
message_order       目前服务端已经传送的消息个数，
                    用于从 1 开始分配消息 ID (1, 2, 3, ...)，区分消息
server_socket       服务端向客户端暴露用于连接的 TCP socket
history             用于记录聊天上下文，在新客户端建立连接时
                    通过协议 3.2 发送给客户端
send_queue          记录需要发送给客户端的信息，
                    数据格式为 str({ "to": UID, "content": JSON })
receive_queue       记录从客户端读取到的（符合协议的）信息，
                    数据格式为 str({ "from": UID, "content": JSON })

对于 users 列表的每个 JSON 项，以下字段在服务端和客户端中均存在：
(index)             每个用户的用户 ID 与对应 JSON 项在列表中的下标相等
username            用户名
status              状态，参见上面对 online_count 变量的说明

对于 users 列表的每个 JSON 项，以下字段在服务端中存在，在客户端中不存在：
body                连接到该用户的 TCP socket
buffer              body 读取时模拟的缓冲区（发送的数据都是 NDJSON，
                    因此遇到换行符则清空）
ip                  数据格式为 [str, int]，
                    ip[0] 为 IPv4 地址，ip[1] 为端口
busy                bool 类型变量，表示服务端是否在向该客户端发送文件：
                    若取值为 True，则阻止第四部分的 thread_check 线程
                    向该用户发送心跳数据（单个换行符），
                    防止 NDJSON 被意外截断
"""
config = DEFAULT_CLIENT_CONFIG
blocked = False
stamp = int(time.time() * (10 ** 6))
my_username = "user"
my_uid = 0
file_order = 0
message_order = 0
my_socket = None
users = []
server_socket = socket.socket()
side = "Server"
server_version = VERSION
history = []
online_count = 1
buffer = ""
bell_countdown = 0
exit_flag = False
log_queue = queue.Queue()
receive_queue = queue.Queue()
send_queue = queue.Queue()
print_queue = queue.Queue()





# ================================ 第二部分：功能性函数 ================================





# 响铃
def ring():
	print("\a", end="", flush=True)

# 清屏
def clear_screen():
	if platform.system() == "Windows":
		os.system("cls")
	else:
		os.system("clear")

# 多行输入
def enter():
	if platform.system() == "Windows":
		shortcut = "C"
	else:
		shortcut = "D"
	print("请输入要发送的消息。")
	print("输入结束后，先按下 Enter，然后按下 Ctrl + {}。".format(shortcut))
	message = ""
	while True:
		try:
			message += input() + "\n"
		except EOFError:
			break
	if message:
		message = message[:-1]
	return message

# 利用 ANSI 转义序列给文本染色，
# 其中 \033[8;30m 用于输出模式下隐藏输入的文本；
# color_code 传入 None 时不额外染色（下同）
def dye(text, color_code):
	if color_code:
		return "\033[0m\033[1;3{}m{}\033[8;30m".format(COLORS[color_code], text)
	return text

# 转换到输出模式时使用，一次性输出所有被阻塞的输出内容
def flush():
	global print_queue
	if not blocked:
		while not print_queue.empty():
			print(print_queue.get())

# 受 blocked 变量控制的文本输出（用于输出一般信息）
def prints(text, color_code=None):
	global print_queue
	if not blocked:
		print(dye(text, color_code))
	else:
		print_queue.put(dye(text, color_code))

# 不受 blocked 变量控制的强制文本输出：
# 只用于 dashboard 指令、flood 指令（部分）
# 和 help 指令输出信息
def printf(text, color_code=None):
	print(dye(text, color_code))

# 用于第三部分的指令函数输出提示信息，
# 根据传入的 verbose 变量决定是否输出指令执行结果提示：
# 用户执行指令时 verbose 变量为 True，输出相应提示信息；
# 随后请求会发给服务端，服务端调用同样的函数进行二次检查，
# 此时 verbose 变量为 False，因此服务端不会看到奇怪的提示信息
def printc(verbose, text):
	if verbose:
		print(dye(text, "black"))

# 解析用户名
def parse_username(arg, expected_status):
	try:
		uid = int(arg.split()[0])
		if uid >= 0 and uid < len(users) and users[uid]["status"] in expected_status:
			return arg
		raise
	except:
		for i in range(len(users)):
			if users[i]["status"] in expected_status:
				if arg.startswith(users[i]["username"] + " ") or arg == users[i]["username"]:
					return str(i) + arg[len(users[i]["username"]):]
		return ""

# 检查 element 是不是合法 IP
def check_ip(element):
	pattern = r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$" # int.int.int.int
	match = re.search(pattern, element)
	if not match:
		return False
	for i in range(1, 5):
		if int(match.group(i)) < 0 or int(match.group(i)) > 255: # x.x.x.x 中 0 <= x <= 255
			return False
	return True

# 检查 element 是不是合法 IP 段，要求前缀长度不小于 24
def check_ip_segment(element):
	if not check_ip(element.split("/")[0]): # 先检查 IP 段前半部分的 IP
		return [] # 返回 [] 表明 IP 段本身不合法
	if not "/" in element:
		element = element + "/32" # 将 x.x.x.x 转换为 x.x.x.x/32 再继续解析
	pattern = r"^(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)$" # int.int.int.int/int
	match = re.search(pattern, element)
	if not match:
		return []
	numbers = [0] + [int(match.group(i)) for i in range(1, 6)]
	if numbers[5] < 0 or numbers[5] > 32: # 0 <= 前缀长度 <= 32
		return []
	if numbers[4] % (2 ** (32 - numbers[5])): # 把 x.x.x.x 转换为网络地址
		numbers[5] -= numbers[4] % (2 ** (32 - numbers[5]))
	if numbers[5] < 24: # 前缀长度 >= 24
		return [""] # 返回 [""] 表明 IP 段本身是合法的，只是前缀长度需要 >= 24
	result = [] # 枚举网络中的所有 IPv4，逐个添加进 ban.ip 参数
	for i in range(numbers[4], numbers[4] + 2 ** (32 - numbers[5])):
		result.append("{}.{}.{}.{}".format(numbers[1], numbers[2], numbers[3], i))
	return result

# 返回一个 "xxxx-xx-xx xx:xx:xx.xxxxxx" 格式的字符串表示当前时区的当前时间；
# 下面的 announce 和 print_message 函数对其切片 [11:19]，
# 可以得到其中的 "xx:xx:xx"
def time_str():
	return str(datetime.datetime.now())

# 公告消息的消息头
def announce(uid):
	first_line = dye("[" + time_str()[11:19] + "]", "black")
	if uid == my_uid:
		first_line += dye(" [您发送的]", "blue")
	first_line += dye(" [公告]", "red")
	first_line += " "
	first_line += dye("@", "black")
	first_line += dye(users[uid]["username"], "yellow")
	first_line += dye(":", "black")
	prints(first_line)

# 其他消息的消息头（根据协议 2.2 进行解析）
def print_message(message):
	global bell_countdown
	first_line = dye("[" + message["time"][11:19] + "]", "black")
	if message["order"] > 0:
		first_line += dye(" (#" + str(message["order"]) + ")", "black")
	if message["from"] == my_uid:
		first_line += dye(" [您发送的]", "blue")
	if message["to"] == my_uid:
		first_line += dye(" [发给您的]", "blue")
	try:
		if message["filename"]:
			first_line += dye(" [文件]", "red")
	except KeyError:
		pass
	if message["to"] == -2:
		first_line += dye(" [广播]", "red")
		# 增加 bell_countdown 的值以请求
		# thread_output 完成额外的 4 次响铃，
		# 由于 thread_output 先将 bell_countdown
		# 减去 1 再判断是否响铃，因此第 2 次
		# 响铃出现在 1.5 秒后 bell_countdown
		# 为 60 的时刻，第 5 次响铃出现在 6 秒后
		# bell_countdown 为 15 的时刻
		bell_countdown += 75
	if message["to"] >= 0:
		first_line += dye(" [私聊]", "green")
	first_line += " "
	first_line += dye("@", "black")
	first_line += dye(users[message["from"]]["username"], "yellow")
	# 对于私聊消息，上面的代码输出发送方，下面的代码输出接收方
	if message["to"] >= 0:
		first_line += dye(" -> ", "green")
		first_line += dye("@", "black")
		first_line += dye(users[message["to"]]["username"], "yellow")
	first_line += dye(":", "black")
	prints(first_line)
	try:
	# 对于文件消息，保存到 TouchFishFiles/<order>.file，
	# 其中 <order> 的定义参见第一部分对 file_order 变量
	# 用途的介绍和协议 2.2 的协议文档，取绝对值
		if message["filename"]:
			# 服务端的文件保存工作已经在第三部分的
			# do_distribute 函数和 do_transfer 函数
			# 完成，因此这里只在角色为客户端时保存文件
			if side == "Client":
				try:
					# 以二进制格式输出 base64 解密后的结果，
					# Windows 下子目录用反斜杠，其他用正斜杠（下同）
					if platform.system() == "Windows":
						with open("TouchFishFiles\\{}\\{}.file".format(stamp, -message["order"]), "wb") as f:
							f.write(base64.b64decode(message["content"]))
					else:
						with open("TouchFishFiles/{}/{}.file".format(stamp, -message["order"]), "wb") as f:
							f.write(base64.b64decode(message["content"]))
				except:
					pass
			prints("发送了文件 {}，已经保存到：TouchFishFiles/{}/{}.file".format(message["filename"], stamp, -message["order"]), "cyan")
		else:
			prints(message["content"], "white")
	except KeyError:
		prints(message["content"], "white") # 对于普通消息，直接显示消息内容

# 处理 my_socket 收到的信息
def process(message):
	global users
	global online_count
	global exit_flag
	ring() # 响铃
	if message["type"] == "CHAT.RECEIVE": # 收到消息 (协议 2.2)
		message["time"] = time_str()
		print_message(message)
		return
	if message["type"] == "GATE.CLIENT_REQUEST.ANNOUNCE": # 新的客户端连接到聊天室 (协议 1.5.1)
		announce(0)
		prints("用户 {} (UID = {}) 请求加入聊天室，请求结果：".format(message["username"], message["uid"]) + message["result"], "cyan")
		if side == "Client": # 同上，客户端已经在别处更新
			users.append({"username": message["username"], "status": "Rejected"})
			if message["result"] == "Pending review":
				users[message["uid"]]["status"] = "Pending"
			if message["result"] == "Accepted":
				users[message["uid"]]["status"] = "Online"
			if side == "Client" and message["result"] in ["Pending review", "Accepted"]: # 同上
				online_count += 1
		return
	if message["type"] == "GATE.STATUS_CHANGE.ANNOUNCE": # 用户状态变更 (协议 1.6.2)
		announce(message["operator"])
		prints("用户 {} (UID = {}) 的状态变更为：".format(users[message["uid"]]["username"], message["uid"]) + message["status"], "cyan")
		if side == "Client": # 同上
			users[message["uid"]]["status"] = message["status"]
			if message["status"] in ["Offline", "Kicked", "Rejected"]:
				online_count -= 1
		if message["uid"] == my_uid and message["status"] == "Kicked": # 特殊情况：自己被踢出
			while blocked:
				pass
			my_socket.close() # 关闭相应 TCP socket
			prints("您被踢出了聊天室。", "cyan")
			# 此处不能调用 dye 函数，因为需要使用 \033[0m
			# 来清除 ANSI 文本序列带来的显示效果，
			# 防止干扰用户后续的终端使用
			prints("\033[0m\033[1;36m再见！\033[0m")
			exit_flag = True
			return
	if message["type"] == "SERVER.CONFIG.CHANGE": # 服务端参数变更 (协议 3.5.2)
		announce(message["operator"])
		prints("配置项 {} 变更为：".format(message["key"]) + str(message["value"]), "cyan")
		if side == "Client": # 同上
			if isinstance(message["value"], list):
				additions = [item for item in message["value"] if not item in config[message["key"].split(".")[0]][message["key"].split(".")[1]]]
				deletions = [item for item in config[message["key"].split(".")[0]][message["key"].split(".")[1]] if not item in message["value"]]
				prints("该配置项相比修改前增加了：{}".format(str(additions)), "cyan")
				prints("该配置项相比修改前移除了：{}".format(str(deletions)), "cyan")
		config[message["key"].split(".")[0]][message["key"].split(".")[1]] = message["value"]
		return
	if message["type"] == "SERVER.STOP.ANNOUNCE": # 服务端关闭 (协议 3.5.1)
		if side == "Client": # 同上
			announce(0)
			prints("聊天室服务端已经关闭。", "cyan")
			prints("\033[0m\033[1;36m再见！\033[0m")
			exit_flag = True
			return

# 从 my_socket 读取数据，每次 128 KiB，读完为止
def read():
	global my_socket
	global buffer
	while True:
		try:
			my_socket.setblocking(False)  # 再次显式设置为非阻塞模式，避免不必要的问题
			chunk = my_socket.recv(131072).decode("utf-8")
			if not chunk:
				break
			buffer += chunk
		except BlockingIOError:
			break
	return None

# 从 buffer 中分离首个 \n（如果有）前的信息，返回解析到的 JSON
def get_message():
	global buffer
	global log_queue
	message = ""
	while not message:
		try:
			message, buffer = buffer.split("\n", 1)
		except:
			return None
	try:
		message = json.loads(message)
	except:
		return None
	try:
		# 检查是否为文件
		if message["filename"]:
			# 如果是文件，则先将文件内容剥离再写入日志
			partial_message = {key: value for key, value in message.items()}
			partial_message["content"] = ""
			log_queue.put(json.dumps(partial_message))
		else:
			# filename 字段为空（或者 filename 字段根本不存在），表明不是文件
			impossible_value = message["impossible_key"] # 故意引发 KeyError
	except KeyError:
		log_queue.put(json.dumps(message)) # 如果不是文件，则直接写入日志
	return message

# 将给定的信息通过 my_socket 发送给服务端
def upload(message):
	global my_socket
	global log_queue
	log_queue.put(json.dumps(message))
	my_socket.send(bytes(json.dumps(message) + "\n", encoding="utf-8"))





# ============================= 第三部分：与指令对应的函数 =============================





# 对于用户直接调用的指令，参数传递规则如下（某些指令只出现部分参数）：
"""
arg         指令参数：紧跟指令后的全部文本，
            如输入 "admin add 1" 则传入 "add 1"
message     消息：固定为 None（缺省值）
verbose     是否为直接调用的指令：固定为 True（缺省值）
by          请求发送者的 UID：固定为 -1（缺省值），
            然后在函数开头赋值为 my_uid
"""
# 调用成功后请求会发到服务端，服务端会重新调用函数，参数传递规则如下：
"""
arg         指令参数：先解析相关协议，
            然后按 HELP_HINT 第 6 段中给出的格式
            复原成字符串后传入函数
message     消息：将相关协议中的消息 (content.content) 字段
            直接传入函数，此时 arg 按照多行输入方法传入函数
verbose     是否为直接调用的指令：固定传入 False
by          请求发送者的 UID：固定传入 receive_queue
            内部 JSON 格式数据中的发送者 (from) 字段，
            然后跳过函数开头的赋值
"""

# 为了确保客户端的各项数据能与服务端正确同步，
# 以下指令函数在客户端均采用异步请求的数据更新方式，
# 所有变量的实际修改以服务端广播的通知为准，
# 而不是在客户端判定指令执行成功并向服务端发送请求时就修改；
# 因此服务端广播任何消息时都不应该将请求发送者排除在广播对象之外

# 对于完全不需要参数的指令 (dashboard, exit, help)，
# 服务端不会重新调用函数（因为根本没有请求），
# 参数中只有一个 arg (缺省为 None，函数中不会调用)，
# 用于在第四部分的 thread_input 线程中统一调用接口

def do_doorman(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global online_count
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]["status"] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(" ", 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	arg[1] = parse_username(arg[1], ["Pending"])
	try:
		arg[1] = int(arg[1])
	except:
		printc(verbose, "参数错误：用户解析失败，只能对状态为 Pending 的用户操作。")
		return
	if not arg[0] in ["accept", "reject"]:
		printc(verbose, "参数错误：第一个参数必须是 accept 和 reject 中的某一项。")
		return

	if side == "Server":
		# 先发送心跳数据（连续 10 个换行符）检查客户端是否下线
		try:
			for _ in range(10):
				users[arg[1]]["body"].send(bytes("\n", encoding="utf-8")) # 协议 4
		except:
			users[arg[1]]["body"].close() # 关闭相应 TCP socket
			users[arg[1]]["status"] = "Offline"
			online_count -= 1
			log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Offline", "uid": arg[1], "operator": 0})) # 协议 1.6.3
			for i in range(len(users)):
				if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Offline", "uid": arg[1], "operator": 0}})) # 协议 1.6.2
			printc(verbose, "操作失败：该用户在操作前已经下线。")
			return
	
	if arg[0] == "accept":
		if side == "Server":
			# 根据协议 3.2 生成适合客户端的 users 字段
			users[arg[1]]["status"] = "Online"
			users_abstract = []
			for i in range(len(users)):
				users_abstract.append({"username": users[i]["username"], "status": users[i]["status"]})
			send_queue.put(json.dumps({"to": arg[1], "content": {"type": "GATE.REVIEW_RESULT", "accepted": True, "operator": {"username": users[by]["username"], "uid": by}}})) # 协议 1.3
			send_queue.put(json.dumps({"to": arg[1], "content": {"type": "SERVER.DATA", "server_version": VERSION, "uid": arg[1], "config": config, "users": users_abstract, "chat_history": history}})) # 协议 3.2
		if side == "Client":
			upload({"type": "GATE.STATUS_CHANGE.REQUEST", "status": "Online", "uid": arg[1]}) # 协议 1.6.1
	
	if arg[0] == "reject":
		if side == "Server":
			users[arg[1]]["status"] = "Rejected"
			users[arg[1]]["body"].send(bytes(json.dumps({"type": "GATE.REVIEW_RESULT", "accepted": False, "operator": {"username": users[by]["username"], "uid": by}}) + "\n", encoding="utf-8")) # 协议 1.3
			log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Rejected", "uid": arg[1], "operator": by})) # 协议 1.6.3
			for i in range(len(users)):
				if users[i]["status"] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Rejected", "uid": arg[1], "operator": by}})) # 协议 1.6.2
			# 关闭相应 TCP socket 并更新在线人数
			users[arg[1]]["body"].close()
			online_count -= 1
		if side == "Client":
			upload({"type": "GATE.STATUS_CHANGE.REQUEST", "status": "Rejected", "uid": arg[1]}) # 协议 1.6.1
	
	printc(verbose, "操作成功。")

def do_kick(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global online_count
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]["status"] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	if not arg:
		printc(verbose, "参数错误：应当给出恰好 1 个参数。")
		return
	arg = parse_username(arg, ["Online", "Admin"])
	try:
		arg = int(arg)
	except:
		printc(verbose, "参数错误：用户解析失败，只能对状态为 Online 或 Admin 的用户操作。")
		return
	if users[by]["status"] == "Admin" and users[arg]["status"] == "Admin":
		printc(verbose, "参数错误：用户解析失败，状态为 Admin 的用户只能对状态为 Online 的用户操作。")
		return
	
	if side == "Server":
		log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Kicked", "uid": arg, "operator": by})) # 协议 1.6.3
		# 被操作的用户的状态即将更新为 Kicked，
		# 不会被下面的 for 循环覆盖，需要单独更新
		users[arg]["status"] = "Kicked"
		try:
			users[arg]["body"].send(bytes(json.dumps({"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Kicked", "uid": arg, "operator": by}) + "\n", encoding="utf-8")) # 协议 1.6.2
		except:
			pass
		users[arg]["body"].close() # 关闭相应 TCP socket
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Kicked", "uid": arg, "operator": by}})) # 协议 1.6.2
		online_count -= 1 # 更新在线人数
	if side == "Client":
		upload({"type": "GATE.STATUS_CHANGE.REQUEST", "status": "Kicked", "uid": arg}) # 协议 1.6.1
	
	printc(verbose, "操作成功。")

def do_admin(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	if by == -1:
		by = my_uid
	if users[by]["status"] != "Root":
		printc(verbose, "只有处于 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(" ", 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	if not arg[0] in ["add", "remove"]:
		printc(verbose, "参数错误：第一个参数必须是 add 或 remove。")
		return
	arg[1] = parse_username(arg[1], ["Online", "Admin"])
	try:
		arg[1] = int(arg[1])
	except:
		if arg[0] == "add":
			printc(verbose, "参数错误：用户解析失败，只能对状态为 Online 的用户操作。")
		if arg[0] == "remove":
			printc(verbose, "参数错误：用户解析失败，只能对状态为 Admin 的用户操作。")
		return
	
	if arg[0] == "add":
		if users[arg[1]]["status"] != "Online":
			printc(verbose, "参数错误：用户解析失败，只能对状态为 Online 的用户操作。")
			return
		users[arg[1]]["status"] = "Admin"
		log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Admin", "uid": arg[1], "operator": by})) # 协议 1.6.3
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Admin", "uid": arg[1], "operator": by}})) # 协议 1.6.2
	
	if arg[0] == "remove":
		if users[arg[1]]["status"] != "Admin":
			printc(verbose, "参数错误：用户解析失败，只能对状态为 Admin 的用户操作。")
			return
		users[arg[1]]["status"] = "Online"
		log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Online", "uid": arg[1], "operator": by})) # 协议 1.6.3
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Online", "uid": arg[1], "operator": by}})) # 协议 1.6.2
	
	printc(verbose, "操作成功。")

def do_config(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global config
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]["status"] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(" ", 1)
	if len(arg) != 2:
		printc(verbose, "参数错误：应当给出恰好 2 个参数。")
		return
	if not arg[0] in CONFIG_TYPE_CHECK_TABLE:
		printc(verbose, "该参数不存在。")
		return
	if arg[0].split(".")[0] == "general":
		printc(verbose, "不允许在指令行内修改该参数，请退出聊天室后重新打开以修改。")
		return
	if verbose:
		if arg[0] == "gate.enter_hint":
			printc(verbose, "请注意，本参数修改时 <value> 需要带引号并转义。")
			printc(verbose, "例如，将进入提示设为英文 Hi there! 并且末尾换行：")
			printc(verbose, r"  config gate.enter_hint 'Hi there!\n'")
			if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ["y", "Y"]:
				return
			print("\033[8;30m", end="", flush=True)
		if arg[0] == "ban.ip" or arg[0] == "ban.words":
			printc(verbose, "请注意，本参数修改时 <value> 需要带引号并转义。")
			printc(verbose, "例如，将 fuck 和 shit 设置为屏蔽词：")
			printc(verbose, r"  config ban.words ['fuck', 'shit']")
			printc(verbose, "该操作将【清空】原有的屏蔽词列表（或 IP 黑名单），请谨慎操作！")
			if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ["y", "Y"]:
				return
			print("\033[8;30m", end="", flush=True)
	
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
				if "\n" in item or "\r" in item or not item:
					printc(verbose, "屏蔽词列表中不能出现空串和换行符。")
					raise
		if arg[0] == "ban.ip":
			for item in eval(arg[1]):
				if not check_ip(item):
					printc(verbose, "IP 黑名单中的元素 {} 不是有效的点分十进制格式 IPv4 地址。".format(item))
					raise
		
		first, second = arg[0].split(".")
		if side == "Server":
			config[first][second] = eval(arg[1])
			log_queue.put(json.dumps({"type": "SERVER.CONFIG.LOG", "time": time_str(), "key": first + "." + second, "value": eval(arg[1]), "operator": by})) # 协议 3.5.4
			for i in range(len(users)):
				if users[i]["status"] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.CONFIG.CHANGE", "key": first + "." + second, "value": eval(arg[1]), "operator": by}})) # 协议 3.5.2
		if side == "Client":
			upload({"type": "SERVER.CONFIG.POST", "key": first + "." + second, "value": eval(arg[1])}) # 协议 3.5.1
	except:
		printc(verbose, "指令格式不正确，请重试。")
		return
	
	printc(verbose, "操作成功。")

def do_ban(arg, verbose=True, by=-1):
	global log_queue
	global send_queue
	global config
	global my_socket
	if by == -1:
		by = my_uid
	if not users[by]["status"] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	arg = arg.split(" ", 2)
	if len(arg) != 3:
		printc(verbose, "参数错误：应当给出恰好 3 个参数。")
		return
	if not arg[0] in ["ip", "words"]:
		printc(verbose, "参数错误：第一个参数必须是 ip 和 words 中的某一项。")
		return
	if not arg[1] in ["add", "remove"]:
		printc(verbose, "参数错误：第二个参数必须是 add 和 remove 中的某一项。")
		return
	
	if arg[0] == "ip":
		ips = check_ip_segment(arg[2])
		if ips == []:
			printc(verbose, "输入数据不是合法的点分十进制格式 IPv4 地址或 IPv4 段。")
			return
		if ips == [""]:
			printc(verbose, "出于性能、安全性和实际使用环境考虑，IPv4 段的前缀长度不得小于 24。")
			return
		
		if arg[1] == "add":
			if side == "Server":
				ips = [item for item in ips if not item in config["ban"]["ip"]]
				config["ban"]["ip"] += ips
				log_queue.put(json.dumps({"type": "SERVER.CONFIG.LOG", "time": time_str(), "key": "ban.ip", "value": config["ban"]["ip"], "operator": by})) # 协议 3.5.4
				for i in range(len(users)):
					if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.CONFIG.CHANGE", "key": "ban.ip", "value": config["ban"]["ip"], "operator": by}})) # 协议 3.5.2
			if side == "Client":
				ips = [item for item in ips if not item in config["ban"]["ip"]]
				new_value = config["ban"]["ip"] + ips
				upload({"type": "SERVER.CONFIG.POST", "key": "ban.ip", "value": new_value}) # 协议 3.5.1
			printc(verbose, "操作成功，共计封禁了 {} 个 IP 地址。".format(len(ips)))
		
		if arg[1] == "remove":
			if side == "Server":
				ips = [item for item in ips if item in config["ban"]["ip"]]
				config["ban"]["ip"] = [item for item in config["ban"]["ip"] if not item in ips]
				log_queue.put(json.dumps({"type": "SERVER.CONFIG.LOG", "time": time_str(), "key": "ban.ip", "value": config["ban"]["ip"], "operator": by})) # 协议 3.5.4
				for i in range(len(users)):
					if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.CONFIG.CHANGE", "key": "ban.ip", "value": config["ban"]["ip"], "operator": by}})) # 协议 3.5.2
			if side == "Client":
				ips = [item for item in ips if item in config["ban"]["ip"]]
				new_value = [item for item in config["ban"]["ip"] if not item in ips]
				upload({"type": "SERVER.CONFIG.POST", "key": "ban.ip", "value": new_value}) # 协议 3.5.1
			printc(verbose, "操作成功，共计解除封禁了 {} 个 IP 地址。".format(len(ips)))
	
	if arg[0] == "words":
		if "\n" in arg[2] or "\r" in arg[2] or not arg[2]:
			printc(verbose, "屏蔽词不能为空串，且不能包含换行符。")
			return
		if " " in arg[2]:
			if verbose:
				printc(verbose, "请注意，您输入的屏蔽词包含空格。")
				printc(verbose, "系统读取到的屏蔽词为（不包含开头的 ^ 符号和结尾的 $ 符号）：")
				printc(verbose, "^", arg[2], "$", sep="")
				if not input("\033[0m\033[1;30m确定要继续吗？[y/N] ") in ["y", "Y"]:
					return
				print("\033[8;30m", end="", flush=True)
		
		if arg[1] == "add":
			if arg[2] in config["ban"]["words"]:
				printc(verbose, "该屏蔽词已经在列表中出现了。")
				return
			if side == "Server":
				config["ban"]["words"].append(arg[2])
				log_queue.put(json.dumps({"type": "SERVER.CONFIG.LOG", "time": time_str(), "key": "ban.words", "value": config["ban"]["words"], "operator": by})) # 协议 3.5.4
				for i in range(len(users)):
					if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.CONFIG.CHANGE", "key": "ban.words", "value": config["ban"]["words"], "operator": by}})) # 协议 3.5.2
			if side == "Client":
				new_value = config["ban"]["words"][:]
				new_value.append(arg[2])
				upload({"type": "SERVER.CONFIG.POST", "key": "ban.words", "value": new_value}) # 协议 3.5.1
			printc(verbose, "操作成功。")
		
		if arg[1] == "remove":
			if not arg[2] in config["ban"]["words"]:
				printc(verbose, "该屏蔽词不在列表中。")
				return
			if side == "Server":
				config["ban"]["words"].remove(arg[2])
				log_queue.put(json.dumps({"type": "SERVER.CONFIG.LOG", "time": time_str(), "key": "ban.words", "value": config["ban"]["words"], "operator": by})) # 协议 3.5.4
				for i in range(len(users)):
					if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.CONFIG.CHANGE", "key": "ban.words", "value": config["ban"]["words"], "operator": by}})) # 协议 3.5.2
			if side == "Client":
				new_value = config["ban"]["words"][:]
				new_value.remove(arg[2])
				upload({"type": "SERVER.CONFIG.POST", "key": "ban.words", "value": new_value}) # 协议 3.5.1
			printc(verbose, "操作成功。")

def do_broadcast(arg, message=None, verbose=True, by=-1):
	global history
	global log_queue
	global send_queue
	global my_socket
	global message_order
	if by == -1:
		by = my_uid
	if not users[by]["status"] in ["Admin", "Root"]:
		printc(verbose, "只有处于 Admin 或 Root 状态的用户有权执行该操作。")
		return
	if message == None:
		# 在同一行带有参数（消息）则将指令识别为单行输入方法，
		# 否则将指令识别为多行输入方法（下同）
		if arg:
			message = arg
		else:
			message = enter()
	
	if side == "Server":
		message_order += 1 # 给该消息分配一个新的编号，从 1 开始递增（下同）
		log_queue.put(json.dumps({"type": "CHAT.LOG", "time": time_str(), "from": by, "order": message_order, "filename": "", "content": message, "to": -2})) # 协议 2.3
		history.append({"time": time_str(), "from": by, "content": message, "to": -2, "order": message_order}) # 公开消息，记入 history 列表
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "CHAT.RECEIVE", "from": by, "order": message_order, "filename": "", "content": message, "to": -2}})) # 协议 2.2
	if side == "Client":
		upload({"type": "CHAT.SEND", "filename": "", "content": message, "to": -2}) # 协议 2.1
	
	printc(verbose, "操作成功。")

def do_send(arg, message=None, verbose=True, by=-1):
	global history
	global log_queue
	global send_queue
	global my_socket
	global message_order
	if by == -1:
		by = my_uid
	if message == None: # 同上，识别调用方法
		if arg:
			message = arg
		else:
			message = enter()
	if not message:
		printc(verbose, "发送失败：消息不能为空。")
		return
	if len(message) > config["message"]["max_length"]:
		printc(verbose, "发送失败：消息太长。")
		return
	for word in config["ban"]["words"]:
		if word in message:
			printc(verbose, "发送失败：消息中包含屏蔽词：" + word)
			return
	
	if side == "Server":
		message_order += 1 # 同上，给该消息分配一个新的编号
		log_queue.put(json.dumps({"type": "CHAT.LOG", "time": time_str(), "from": by, "order": message_order, "filename": "", "content": message, "to": -1})) # 协议 2.3
		history.append({"time": time_str(), "from": by, "content": message, "to": -1, "order": message_order}) # 公开消息，记入 history 列表
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "CHAT.RECEIVE", "from": by, "order": message_order, "filename": "", "content": message, "to": -1}})) # 协议 2.2
	if side == "Client":
		upload({"type": "CHAT.SEND", "filename": "", "content": message, "to": -1}) # 协议 2.1
	
	printc(verbose, "发送成功。")

def do_whisper(arg, message=None, verbose=True, by=-1):
	global log_queue
	global send_queue
	global my_socket
	global message_order
	if by == -1:
		by = my_uid
	if not config["message"]["allow_private"]:
		printc(verbose, "此聊天室目前不允许发送私聊消息。")
		return
	arg = parse_username(arg, ["Online", "Admin", "Root"])
	# 分离接收方 UID 和（可能不存在的）单行消息
	try:
		arg, message = arg.split(" ", 1)
	except:
		pass
	try:
		arg = int(arg)
	except:
		printc(verbose, "参数错误：用户解析失败，只能对状态处于 Online、Admin、Root 中的某一项的用户操作。")
		return
	if arg == by:
		printc(verbose, "不能向自己发送私聊消息。")
		return
	if message == None: # 同上，识别调用方法
		message = enter()
	if not message:
		printc(verbose, "发送失败：消息不能为空。")
		return
	if len(message) > config["message"]["max_length"]:
		printc(verbose, "发送失败：消息太长。")
		return
	for word in config["ban"]["words"]:
		if word in message:
			printc(verbose, "发送失败：消息中包含屏蔽词：" + word)
			return
	
	if side == "Server":
		# 非公开消息，不记入 history 列表，
		# 于是这里没有了 history.append 语句
		message_order += 1 # 同上，给该消息分配一个新的编号
		log_queue.put(json.dumps({"type": "CHAT.LOG", "time": time_str(), "from": by, "order": message_order, "filename": "", "content": message, "to": arg})) # 协议 2.3
		for i in range(len(users)):
			# 私聊消息只对收发方，状态为 Admin 的用户和
			# 状态为 Root 的用户可见
			if users[i]["status"] in ["Admin", "Root"] or i == by or i == arg:
				send_queue.put(json.dumps({"to": i, "content": {"type": "CHAT.RECEIVE", "from": by, "order": message_order, "filename": "", "content": message, "to": arg}})) # 协议 2.2
	if side == "Client":
		upload({"type": "CHAT.SEND", "filename": "", "content": message, "to": arg}) # 协议 2.1
	
	printc(verbose, "发送成功。")

def do_distribute(arg, message=None, verbose=True, by=-1):
	global log_queue
	global send_queue
	global my_socket
	global file_order
	if by == -1:
		by = my_uid
	if not config["file"]["allow_any"]:
		printc(verbose, "此聊天室目前不允许发送文件。")
		return
	for word in config["ban"]["words"]:
		if word in arg:
			printc(verbose, "发送失败：文件名中包含屏蔽词：" + word)
			return
	# 服务端调用函数时，从协议中传过来的 message 字段
	# 本身就是 base64 加密过的数据，因此跳过重复的加密操作（下同）
	if not message:
		try:
			# 以二进制读取文件，然后转换为 base64（下同）
			with open(arg, "rb") as f:
				file_data = f.read()
			message = base64.b64encode(file_data).decode("utf-8")
		except:
			printc(verbose, "无法读取对应文件。")
			return
	# 用 base64 编码串的长度计算原文件大小，
	# 由于 base64 本身的特性，
	# 计算出的大小会向上取整到 3 的倍数，
	# 这相当于 file.max_size 向下取整到 3 的倍数（下同）
	if len(message) * 3 // 4 > config["file"]["max_size"]:
		printc(verbose, "发送失败：文件太大。")
		return
	
	if side == "Server":
		file_order -= 1 # 给该文件分配一个新的编号，从 -1 开始递减（下同）
		# 服务端在此处接收文件（下同）；
		# 先写入到磁盘（相当于写入日志，尽快释放内存，且减小意外断电的情况下的损失），
		# 然后在第四部分的 thread_send 线程中重新读取并发送
		try:
			# 同上，不同系统的目录格式不同
			if platform.system() == "Windows":
				with open("TouchFishFiles\\{}\\{}.file".format(stamp, -file_order), "wb") as f:
					f.write(base64.b64decode(message))
			else:
				with open("TouchFishFiles/{}/{}.file".format(stamp, -file_order), "wb") as f:
					f.write(base64.b64decode(message))
		except:
			pass
		# 同上，不同系统的目录格式不同
		if platform.system() == "Windows":
			tmp_filename = "TouchFishFiles\\{}\\{}.file".format(stamp, -file_order)
		else:
			tmp_filename = "TouchFishFiles/{}/{}.file".format(stamp, -file_order)
		log_queue.put(json.dumps({"type": "CHAT.LOG", "time": time_str(), "from": by, "order": file_order, "filename": arg, "content": "", "to": -1})) # 协议 2.3
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				# 先以保存文件时使用的文件名填充 content 字段（下同），
				# 该字段稍后会在第四部分的 thread_send 线程中
				# 被覆写为正确值（文件的 base64 编码）
				send_queue.put(json.dumps({"to": i, "content": {"type": "CHAT.RECEIVE", "from": by, "order": file_order, "filename": arg, "content": tmp_filename, "to": -1}})) # 协议 2.2
	if side == "Client":
		# 协议 2.1
		token = json.dumps({"type": "CHAT.SEND", "filename": arg, "content": message, "to": -1}) + "\n"
		chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
		# 分段发送数据，每 32 KiB 一段（下同）
		for chunk in chunks:
			while True:
				try:
					my_socket.send(bytes(chunk, encoding="utf-8"))
					break
				except BlockingIOError:
					# 非阻塞式 TCP socket 遇到 BlockingIOError
					# 是正常的，重新尝试发送即可（下同）
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
	if not config["file"]["allow_any"]:
		printc(verbose, "此聊天室目前不允许发送文件。")
		return
	if not config["file"]["allow_private"]:
		printc(verbose, "此聊天室目前不允许发送私有文件。")
		return
	arg = parse_username(arg, ["Online", "Admin", "Root"])
	# 分离接收方 UID 和（可能不存在的）文件名
	try:
		arg, filename = arg.split(" ", 1)
	except:
		pass
	try:
		arg = int(arg)
	except:
		printc(verbose, "参数错误：用户解析失败，只能对状态处于 Online、Admin、Root 中的某一项的用户操作。")
		return
	if not users[arg]["status"] in ["Online", "Admin", "Root"]:
		printc(verbose, "只能向状态处于 Online、Admin、Root 中的某一项的用户发送私有文件。")
		return
	if arg == by:
		printc(verbose, "不能向自己发送私有文件。")
		return
	for word in config["ban"]["words"]:
		if word in filename:
			printc(verbose, "发送失败：文件名中包含屏蔽词：" + word)
			return
	if not message: # 同上，跳过重复的加密操作
		try:
			# 同上，读取文件并转换
			with open(filename, "rb") as f:
				file_data = f.read()
			message = base64.b64encode(file_data).decode("utf-8")
		except:
			printc(verbose, "无法读取对应文件。")
			return
	if len(message) * 3 // 4 > config["file"]["max_size"]: # 同上，计算原文件大小
		printc(verbose, "发送失败：文件太大。")
		return
	
	if side == "Server":
		file_order -= 1 # 同上，给该文件分配一个新的编号
		# 同上，服务端在此处接收文件
		try:
			# 同上，不同系统的目录格式不同
			if platform.system() == "Windows":
				with open("TouchFishFiles\\{}\\{}.file".format(stamp, -file_order), "wb") as f:
					f.write(base64.b64decode(message))
			else:
				with open("TouchFishFiles/{}/{}.file".format(stamp, -file_order), "wb") as f:
					f.write(base64.b64decode(message))
		except:
			pass
		# 同上，不同系统的目录格式不同
		if platform.system() == "Windows":
			tmp_filename = "TouchFishFiles\\{}\\{}.file".format(stamp, -file_order)
		else:
			tmp_filename = "TouchFishFiles/{}/{}.file".format(stamp, -file_order)
		log_queue.put(json.dumps({"type": "CHAT.LOG", "time": time_str(), "from": by, "order": file_order, "filename": filename, "content": "", "to": arg})) # 协议 2.3
		for i in range(len(users)):
			# 同上，先以保存文件时使用的文件名填充 content 字段；
			# 私有文件只对收发方，状态为 Admin 的用户和
			# 状态为 Root 的用户可见
			if users[i]["status"] in ["Admin", "Root"] or i == by or i == arg:
				send_queue.put(json.dumps({"to": i, "content": {"type": "CHAT.RECEIVE", "from": by, "order": file_order, "filename": filename, "content": tmp_filename, "to": arg}})) # 协议 2.2
	if side == "Client":
		# 协议 2.1
		token = json.dumps({"type": "CHAT.SEND", "filename": filename, "content": message, "to": arg}) + "\n"
		chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
		# 同上，分段发送数据
		for chunk in chunks:
			while True:
				try:
					my_socket.send(bytes(chunk, encoding="utf-8"))
					break
				except BlockingIOError:
					# 同上，重新尝试发送即可
					continue
				except Exception as e:
					printc(verbose, "发送失败：{}".format(e))
					return
	
	printc(verbose, "发送成功。")

def do_dashboard(arg=None):
	printf("=" * 76, "black")
	printf("服务端版本：" + server_version, "black")
	printf("您的 UID：" + str(my_uid), "black")
	printf("您的状态：" + users[my_uid]["status"], "black")
	printf("在线人数：{} / {}".format(online_count, config["general"]["max_connections"]), "black")
	printf("聊天室参数及具体用户信息详见下表。", "black")
	printf("=" * 76, "black")
	printf(CONFIG_LIST.format(config["gate"]["enter_check"], \
		config["message"]["allow_private"], config["message"]["max_length"], \
		config["file"]["allow_any"], config["file"]["allow_private"], \
		config["file"]["max_size"], config["ban"]["ip"], config["ban"]["words"], \
		config["gate"]["enter_hint"]), "black")
	printf("=" * 76, "black")
	if "ip" in users[0]:
		printf(" UID  IP                        状态      用户名", "black")
		for i in range(len(users)):
			printf("{:>4}  {:<26}{:<10}{}".format(i, "{}:{}".format(users[i]["ip"][0], users[i]["ip"][1]), users[i]["status"], users[i]["username"]), "black")
	else:
		printf(" UID  状态      用户名", "black")
		for i in range(len(users)):
			printf("{:>4}  {:<10}{}".format(i, users[i]["status"], users[i]["username"]), "black")
	printf("=" * 76, "black")

def do_save(arg=None):
	global log_queue
	if users[my_uid]["status"] != "Root":
		print("只有处于 Root 状态的用户有权执行该操作。")
		return
	try:
		with open("./config.json", "w", encoding="utf-8") as f:
			json.dump(config, f)
		print("参数已经成功保存到配置文件 config.json，下次启动时将自动加载配置项。")
		log_queue.put(json.dumps({"type": "SERVER.CONFIG.SAVE", "time": time_str()})) # 协议 3.5.3
	except:
		print("无法将参数保存到配置文件 config.json，请稍后重试。")

def do_evaluate(arg=None):
	try:
		print(eval(arg))
	except Exception as e:
		print("计算时遇到错误：" + str(e))

def do_exit(arg=None):
	global log_queue
	global send_queue
	global exit_flag
	# 此处不能调用 dye 函数，因为需要使用 \033[0m
	# 来清除 ANSI 文本序列带来的显示效果，
	# 防止干扰用户后续的终端使用
	print("\033[0m\033[1;36m再见！\033[0m")
	log_queue.put(json.dumps({"type": "SERVER.STOP.LOG", "time": time_str()})) # 协议 3.4.2
	if side == "Server":
		for i in range(len(users)):
			if users[i]["status"] in ["Pending", "Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "SERVER.STOP.ANNOUNCE"}})) # 协议 3.4.1
		server_socket.close()
	exit_flag = True
	my_socket.close()
	return

def do_flood(arg=None):
	global blocked
	global exit_flag
	if platform.system() == "Windows":
		shortcut = "C"
	else:
		shortcut = "D"
	print(SIMPLE_COMMAND_LINE_HINT_CONTENT.format(shortcut))
	print("\033[8;30m", end="", flush=True)
	while True:
		time.sleep(0.1)
		if exit_flag:
			print("\033[0m", end="", flush=True)
			return
		
		# 输出模式
		try:
			input()
		except EOFError:
			printf("您已经退出简易命令行模式。", "black")
			return
		except:
			pass
		
		# 变更为输入模式
		blocked = True
		try:
			message = input("\033[0m\033[1;30m> ")
		except EOFError:
			print()
			printf("您已经退出简易命令行模式。", "black")
			return
		except:
			pass
		if not message:
			print("\033[8;30m", end="", flush=True)
			blocked = False
			continue
		
		# 发送消息
		do_send(message, None, False, -1)
		print("\033[8;30m", end="", flush=True)
		
		# 变更为输出模式
		blocked = False

def do_help(arg=None):
	print()
	for hint in HELP_HINT:
		printf(hint["content"], hint["color"])
		print()

def do_shell(arg=None):
	print("\033[0m", end="", flush=True) # 执行前清除现有文本效果
	os.system(arg)
	print("\033[8;30m", end="", flush=True) # 执行后恢复现有文本效果





# ============================= 第四部分：与线程对应的函数 =============================





"""
以下线程同时在客户端和服务端启用：
thread_input        读取用户输入
thread_output       打印内容到控制台
thread_log          处理各函数放入到 log_queue 的日志写入请求
以下线程只在服务端启用，客户端不启用：
thread_gate         处理新的客户端连接
thread_process      处理 receive_queue 中的请求
thread_receive      接收客户端请求并放入 receive_queue
thread_send         处理各函数放入到 send_queue 的消息发送请求
thread_check        轮番检查各客户端是否下线，并给服务端保活
"""

# 所有线程均使用 while True 的无限循环，
# 每轮开始前暂停 0.1 秒防止 CPU 占用过高，
# 且均受程序终止信号 exit_flag 的调控

def thread_gate():
	global online_count
	global log_queue
	global send_queue
	global users
	while True:
		time.sleep(0.1)
		if exit_flag:
			return
		
		# 尝试开启新连接
		conntmp, addresstmp = None, None
		try:
			conntmp, addresstmp = server_socket.accept()
			# 调整为非阻塞模式（下同），缓冲区大小设置为 1 MiB，改善性能
			conntmp.setblocking(False)
			conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
			conntmp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
		except:
			continue
		
		time.sleep(0.5) # 等待 0.5 秒，预防网络延迟带来的问题
		# 核验协议 1.1
		data = ""
		while True:
			try:
				conntmp.setblocking(False) # 再次显式设置为非阻塞模式，避免不必要的问题
				chunk = conntmp.recv(131072).decode("utf-8")
				if not chunk:
					raise
				data += chunk
			except:
				break
		
		try:
			data = json.loads(data)
			if data["type"] != "GATE.REQUEST" or not isinstance(data["username"], str) or not data["username"]:
				raise
		except:
			for method in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]: # 检查是否为 HTTP 请求
				if method in data:
					try:
						conntmp.send(bytes(WEBPAGE_CONTENT, encoding="utf-8")) # 返回 HTML 提示页面
						break
					except:
						pass
			log_queue.put(json.dumps({"type": "GATE.INCORRECT_PROTOCOL", "time": time_str(), "ip": addresstmp})) # 协议 1.4
			conntmp.close() # 关闭相应 TCP socket
			continue
		
		# 分配用户 ID
		uid = len(users)
		users.append({"body": conntmp, "buffer": "", "ip": addresstmp, "username": data["username"], "status": "Pending", "busy": False}) # 更新用户列表
		# 加入检查
		result = "Accepted"
		if config["gate"]["enter_check"]:
			result = "Pending review"
		if users[uid]["ip"][0] in config["ban"]["ip"]:
			result = "IP is banned"
		if online_count == config["general"]["max_connections"]:
			result = "Room is full"
		for user in users[:-1]:
			if user["status"] in ["Online", "Admin", "Root", "Pending"] and users[uid]["username"] == user["username"]:
				result = "Duplicate usernames"
		for word in config["ban"]["words"]:
			if word in users[uid]["username"]:
				result = "Username consists of banned words"
		
		while True:
			try:
				users[uid]["body"].send(bytes(json.dumps({"type": "GATE.RESPONSE", "result": result}) + "\n", encoding="utf-8")) # 协议 1.2
				break
			except BlockingIOError:
				continue
			except:
				break
		
		log_queue.put(json.dumps({"type": "GATE.CLIENT_REQUEST.LOG", "time": time_str(), "ip": users[uid]["ip"], "username": users[uid]["username"], "uid": uid, "result": result})) # 协议 1.5.2
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.CLIENT_REQUEST.ANNOUNCE", "username": users[uid]["username"], "uid": uid, "result": result}})) # 协议 1.5.1
		
		if not result in ["Accepted", "Pending review"]:
			users[uid]["status"] = "Rejected"
			users[uid]["body"].close() # 关闭相应 TCP socket
			continue
		# 设置 TCP 保活参数（下同）：启用功能，5 分钟后开始探测，间隔 30 秒
		if platform.system() != "Windows":
			users[uid]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
			users[uid]["body"].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 300)
			users[uid]["body"].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
		else:
			users[uid]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
			users[uid]["body"].ioctl(socket.SIO_KEEPALIVE_VALS, (1, 300000, 30000))
		online_count += 1
		
		if result == "Accepted":
			users[uid]["status"] = "Online"
			users_abstract = []
			for i in range(len(users)):
				users_abstract.append({"username": users[i]["username"], "status": users[i]["status"]})
			send_queue.put(json.dumps({"to": uid, "content": {"type": "SERVER.DATA", "server_version": VERSION, "uid": uid, "config": config, "users": users_abstract, "chat_history": history}})) # 协议 3.2

def thread_process():
	global online_count
	global receive_queue
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(0.1)
		if exit_flag:
			return
		
		while not receive_queue.empty():
			message = json.loads(receive_queue.get())
			sender, content = message["from"], message["content"]
			if content["type"] == "CHAT.SEND": # 协议 2.1
				if not content["filename"]:
					if content["to"] == -2:
						do_broadcast(None, content["content"], False, sender)
					if content["to"] == -1:
						do_send(None, content["content"], False, sender)
					if content["to"] >= 0:
						do_whisper(str(content["to"]), content["content"], False, sender)
				else:
					if content["to"] == -1:
						do_distribute(content["filename"], content["content"], False, sender)
					else:
						do_transfer(str(content["to"]) + " " + content["filename"], content["content"], False, sender)
			if content["type"] == "GATE.STATUS_CHANGE.REQUEST": # 协议 1.6.1
				if content["status"] == "Kicked":
					do_kick(str(content["uid"]), False, sender)
				if content["status"] == "Rejected":
					do_doorman("reject " + str(content["uid"]), False, sender)
				if content["status"] == "Online":
					do_doorman("accept " + str(content["uid"]), False, sender)
			if content["type"] == "SERVER.CONFIG.POST": # 协议 3.5.1
				do_config("{} {}".format(content["key"], repr(content["value"])), False, sender)

def thread_receive():
	global receive_queue
	global users
	while True:
		time.sleep(0.1)
		if exit_flag:
			return
		
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"]:
				data = ""
				while True:
					try:
						users[i]["body"].setblocking(False) # 再次显式设置为非阻塞模式，避免不必要的问题
						chunk = users[i]["body"].recv(131072).decode("utf-8")
						if not chunk:
							raise
						data += chunk
					except:
						break
				users[i]["buffer"] += data
				while "\n" in users[i]["buffer"]: # NDJSON 以换行符作为 JSON 分隔标志
					try:
						message, users[i]["buffer"] = users[i]["buffer"].split("\n", 1)
					except:
						message, users[i]["buffer"] = users[i]["buffer"], ""
					# 能解析的交给 thread_process 处理，不能解析的直接丢弃
					try:
						message = json.loads(message)
						if not message["type"]:
							raise
					except:
						continue
					receive_queue.put(json.dumps({"from": i, "content": message}))

def thread_send():
	global online_count
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(0.1)
		if exit_flag:
			return
		
		while not send_queue.empty():
			message = json.loads(send_queue.get())
			if not users[message["to"]]["status"] in ["Online", "Admin", "Root", "Pending"]:
				continue
			# 先发送心跳数据（连续 10 个换行符）检查客户端是否下线
			try:
				for _ in range(10):
					users[message["to"]]["body"].send(bytes("\n", encoding="utf-8"))# 协议 4
			except:
				users[message["to"]]["body"].close() # 关闭相应 TCP socket
				users[message["to"]]["status"] = "Offline"
				online_count -= 1
				log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Offline", "uid": message["to"], "operator": 0})) # 协议 1.6.3
				for i in range(len(users)):
					if users[i]["status"] in ["Online", "Admin", "Root"]:
						send_queue.put(json.dumps({"to": i, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Offline", "uid": message["to"], "operator": 0}})) # 协议 1.6.2
			try:
				# 先按文件处理
				if not message["content"]["filename"]: # filename 字段为空（或者 filename 字段根本不存在），表明不是文件
					impossible_value = message["content"]["impossible_key"] # 故意引发 KeyError
				with open(message["content"]["content"], "rb") as f:
					file_data = f.read() # 读取 do_distribute 或 do_transfer 函数先前写入到磁盘的对应文件
				message["content"]["content"] = base64.b64encode(file_data).decode("utf-8") # 将 content 字段覆写为正确值
				token = json.dumps(message["content"]) + "\n"
				# 同上，分段发送数据
				chunks = [token[i:i+32768] for i in range(0, len(token), 32768)]
				users[message["to"]]["busy"] = True # 先通知 thread_check 暂停发送心跳数据（单个换行符），防止 NDJSON 被意外截断
				time.sleep(0.1) # 等待 0.1 秒以规避竞态数据问题（下同）
				for chunk in chunks:
					while True:
						try:
							users[message["to"]]["body"].send(bytes(chunk, encoding="utf-8"))
							break
						except BlockingIOError:
							continue
						except:
							break
				time.sleep(0.1) # 同上，等待 0.1 秒以规避竞态数据问题
				users[message["to"]]["busy"] = False
			except KeyError:
				# 不是文件，按普通消息处理
				users[message["to"]]["busy"] = False # 不用担心被截断了
				# 不分段，直接发送
				try:
					users[message["to"]]["body"].send(bytes(json.dumps(message["content"]) + "\n", encoding="utf-8"))
				except:
					pass

def thread_log():
	global log_queue
	while True:
		time.sleep(1) # 该部分不是主要业务流程，因此执行频率下调至 1 秒一次
		if not log_queue.empty():
			with open("./log.ndjson", "a", encoding="utf-8") as file: # 追加写入到 log.ndjson
				while not log_queue.empty():
					file.write(log_queue.get() + "\n")
		# 与其他线程不同，先写入日志再读取程序终止信号，
		# 确保程序终止时没有日志残留在 log_queue 中
		if exit_flag:
			return

def thread_check():
	global online_count
	global send_queue
	global log_queue
	global users
	while True:
		time.sleep(1) # 该部分对整体性能影响较大，因此执行频率下调至 1 秒一次
		if exit_flag:
			return
		
		down = []
		# 先完成全部下线用户检测工作再一并广播，
		# 避免将状态变更通知（不必要地）发送给
		# 同一轮检测中被检测到下线的用户
		for i in range(len(users)):
			if users[i]["status"] in ["Online", "Admin", "Root"] and not users[i]["busy"]:
				try:
					# 发送心跳数据（连续 10 个换行符）
					for _ in range(10):
						users[i]["body"].send(bytes("\n", encoding="utf-8")) # 协议 4
				except:
					users[i]["body"].close() # 关闭相应 TCP socket
					users[i]["status"] = "Offline"
					down.append(i)
					online_count -= 1
					log_queue.put(json.dumps({"type": "GATE.STATUS_CHANGE.LOG", "time": time_str(), "status": "Offline", "uid": i, "operator": 0})) # 协议 1.6.3
		for i in down:
			for j in range(len(users)):
				if users[j]["status"] in ["Online", "Admin", "Root"]:
					send_queue.put(json.dumps({"to": j, "content": {"type": "GATE.STATUS_CHANGE.ANNOUNCE", "status": "Offline", "uid": i, "operator": 0}})) # 协议 1.6.2

def thread_input():
	global blocked
	global exit_flag
	global log_queue
	while True:
		time.sleep(0.1)
		if exit_flag:
			print("\033[0m", end="", flush=True)
			return
		
		# 输出模式
		try:
			input()
		except:
			pass
		
		# 变更为输入模式
		blocked = True
		try:
			command = input("\033[0m\033[1;30m> ")
		except:
			pass
		if not command:
			print("\033[8;30m", end="", flush=True)
			blocked = False
			continue
		log_queue.put(json.dumps({"type": "SERVER.COMMAND", "time": time_str(), "command": command})) # 协议 3.3
		
		# 将缩写形式替换为完整形式
		for i in list(ABBREVIATION_TABLE.keys()):
			if command.startswith(i + " ") or command == i:
				command = ABBREVIATION_TABLE[i] + command[len(i):]
				break
		command = command.split(" ", 1)
		if len(command) == 1:
			command = [command[0], ""]
		if not command[0] in COMMAND_LIST:
			print("指令输入错误。\n\033[8;30m", end="", flush=True)
			blocked = False
			continue
		
		# 将对应指令函数加载到 now，然后执行 now 函数
		now = eval("do_{}".format(command[0]))
		now(command[1])
		print("\033[8;30m", end="", flush=True)
		
		# 变更为输出模式
		blocked = False

def thread_output():
	global bell_countdown
	global exit_flag
	while True:
		time.sleep(0.1)
		if exit_flag:
			print("\033[0m", end="", flush=True)
			return
		
		if bell_countdown:
			bell_countdown -= 1
		if bell_countdown and bell_countdown % 15 == 0:
			ring()
		
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
	global stamp
	global my_username
	global my_uid
	global file_order
	global message_order
	global my_socket
	global users
	global server_socket
	global side
	global server_version
	global history
	global online_count
	global buffer
	global bell_countdown
	global exit_flag
	global log_queue
	global receive_queue
	global send_queue
	global print_queue
	
	# 尝试读取配置文件 (config.json)，
	# 检查规则详见第一部分的相关注释；
	# 检查不通过则加载默认客户端配置
	try:
		with open("./config.json", "r", encoding="utf-8") as f:
			tmp_config = json.load(f)
			if not tmp_config["side"] in ["Server", "Client"]:
				raise
			if tmp_config["side"] == "Server":
				for item, type in CONFIG_TYPE_CHECK_TABLE.items():
					first, second = item.split(".")
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
							if "\n" in element or "\r" in element or not element:
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
			if tmp_config["side"] == "Client":
				if not isinstance(tmp_config["ip"], str):
					raise
				if not isinstance(tmp_config["port"], int):
					raise
				if not isinstance(tmp_config["username"], str):
					raise
				if int(tmp_config["port"]) > 65535:
					raise
				if not tmp_config["username"]:
					raise
				if not tmp_config["ip"]:
					raise
				config = tmp_config
		config_read_result = "OK"
	except FileNotFoundError:
		config = DEFAULT_CLIENT_CONFIG
		config_read_result = "Not found"
	except:
		config = DEFAULT_CLIENT_CONFIG
		config_read_result = "Broken"
	
	os.system("") # 对 Windows 尝试开启 ANSI 转义字符（带颜色文本）支持
	clear_screen()
	
	prints("我们即将推出 TouchFish v5，敬请期待！", "magenta")
	prints("服务端 Github 仓库：https://github.com/2044-space-elevator/TFV5_server", "magenta")
	prints("客户端 Github 仓库：https://github.com/ILoveScratch2/TouchFish-Client", "magenta")
	print()
	
	if config_read_result == "OK":
		prints("配置文件 config.json 读取成功！", "yellow")
	if config_read_result == "Not found":
		prints("未找到配置文件 config.json。如果该文件存在，请尝试以管理员权限重新运行。", "yellow")
		prints("下面将使用默认客户端配置启动程序。", "yellow")
	if config_read_result == "Broken":
		prints("配置文件 config.json 中的配置项存在错误。", "yellow")
		prints("下面将使用默认客户端配置启动程序。", "yellow")
	print()
	
	if platform.system() == "Windows":
		shortcut = "C"
	else:
		shortcut = "D"
	prints("欢迎使用 TouchFish 聊天室！", "yellow")
	prints("当前程序版本：{}".format(VERSION), "yellow")
	prints("按下 Ctrl + {} 以按照配置文件中的配置自动启动。".format(shortcut), "yellow")
	prints("按下 Enter 以指定启动配置。", "yellow")
	
	try:
		auto_start = False
		try:
			input()
		except BaseException as e:
			auto_start = True
		except:
			pass
		tmp_side = None
		if not auto_start:
			tmp_side = input("\033[0m\033[1;37m启动类型 (Server = 服务端, Client = 客户端) [{}]：".format(config["side"]))
		if not tmp_side:
			tmp_side = config["side"]
		if not tmp_side in ["Server", "Client"]:
			prints("参数错误。", "red")
			input("\033[0m")
			sys.exit(1)
			
		if tmp_side == "Server":
			# 当程序以服务端启动时，
			# 若 config.json 中加载到的 side 参数为 "Client"，
			# 则覆写为默认服务端配置
			if config["side"] == "Client":
				config = DEFAULT_SERVER_CONFIG
			tmp_ip = None
			if not auto_start:
				tmp_ip = input("\033[0m\033[1;37m服务端地址 [{}]：".format(config["general"]["server_ip"]))
			if not tmp_ip:
				tmp_ip = config["general"]["server_ip"]
			config["general"]["server_ip"] = tmp_ip
			if not check_ip(tmp_ip):
				prints("参数错误：输入的服务端地址不是有效的点分十进制格式 IPv4 地址。", "red")
				input("\033[0m")
				sys.exit(1)
			tmp_port = None
			if not auto_start:
				tmp_port = input("\033[0m\033[1;37m端口 [{}]：".format(config["general"]["server_port"]))
			if not tmp_port:
				tmp_port = config["general"]["server_port"]
			try:
				tmp_port = int(tmp_port)
				if tmp_port < 1 or tmp_port > 65535:
					raise
			except:
				prints("参数错误：端口号应为不大于 65535 的正整数。", "red")
				input("\033[0m")
				sys.exit(1)
			config["general"]["server_port"] = tmp_port
			tmp_server_username = None
			if not auto_start:
				tmp_server_username = input("\033[0m\033[1;37m服务端管理员的用户名 [{}]：".format(config["general"]["server_username"]))
			if not tmp_server_username:
				tmp_server_username = config["general"]["server_username"]
			config["general"]["server_username"] = tmp_server_username
			my_username = config["general"]["server_username"]
			tmp_max_connections = None
			if not auto_start:
				tmp_max_connections = input("\033[0m\033[1;37m最大在线连接数 [{}]：".format(config["general"]["max_connections"]))
			if not tmp_max_connections:
				tmp_max_connections = config["general"]["max_connections"]
			try:
				tmp_max_connections = int(tmp_max_connections)
				if tmp_max_connections < 1 or tmp_max_connections > 128:
					raise
			except:
				prints("参数错误：最大在线连接数应为不大于 128 的正整数。", "red")
				input("\033[0m")
				sys.exit(1)
			config["general"]["max_connections"] = tmp_max_connections
			
			# 创建保存文件时使用的目录（下同）
			if platform.system() == "Windows":
				os.system("mkdir TouchFishFiles 1>nul 2>&1")
				os.system("mkdir TouchFishFiles\\{} 1>nul 2>&1".format(stamp))
			else:
				os.system("mkdir TouchFishFiles 1>/dev/null 2>&1")
				os.system("mkdir TouchFishFiles/{} 1>/dev/null 2>&1".format(stamp))
			try:
				with open("./config.json", "w", encoding="utf-8") as f:
					json.dump(config, f)
				prints("本次连接中输入的参数已经保存到配置文件 config.json，下次连接时将自动加载。", "yellow")
			except:
				prints("启动时遇到错误：配置文件 config.json 写入失败。", "red")
				input("\033[0m")
				sys.exit(1)
			try:
				with open("./log.ndjson", "a", encoding="utf-8") as f:
					pass
			except:
				prints("启动时遇到错误：无法向日志文件 log.ndjson 写入内容。", "red")
				input("\033[0m")
				sys.exit(1)
			
			try:
				# 启动服务端 socket：
				# 每两步操作之间间隔 0.01 秒，
				# 防止爆出 BlockingIOError
				server_socket = socket.socket()
				time.sleep(0.01)
				server_socket.bind((config["general"]["server_ip"], config["general"]["server_port"]))
				time.sleep(0.01)
				server_socket.listen(config["general"]["max_connections"])
				time.sleep(0.01)
				server_socket.setblocking(False)
				time.sleep(0.01)
				users = [{"body": None, "buffer": "", "ip": None, "username": config["general"]["server_username"], "status": "Root", "busy": False}] # 初始化用户列表
				time.sleep(0.01)
				root_socket = socket.socket() # 为服务端创建一个连接用于接收信息（不用于发送请求）
				time.sleep(0.01)
				root_socket.connect((config["general"]["server_ip"], config["general"]["server_port"])) # 连接到服务端 socket
				time.sleep(0.01)
				# 同上，调整为非阻塞模式，缓冲区大小设置为 1 MiB，改善性能
				root_socket.setblocking(False)
				time.sleep(0.01)
				root_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
				time.sleep(0.01)
				root_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
				time.sleep(0.01)
				users[0]["body"], users[0]["ip"] = server_socket.accept() # 完成连接
				time.sleep(0.01)
				# 同上，设置 TCP 保活参数：启用功能，5 分钟后开始探测，间隔 30 秒
				if platform.system() != "Windows":
					users[0]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
					time.sleep(0.01)
					users[0]["body"].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 300)
					time.sleep(0.01)
					users[0]["body"].setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
					time.sleep(0.01)
				else:
					users[0]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
					time.sleep(0.01)
					users[0]["body"].ioctl(socket.SIO_KEEPALIVE_VALS, (1, 300000, 30000))
					time.sleep(0.01)
					users[0]["body"].setblocking(False)
					time.sleep(0.01)
					users[0]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
					time.sleep(0.01)
				users[0]["body"].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
				time.sleep(0.01)
				my_uid = 0
				time.sleep(0.01)
				my_socket = root_socket
				time.sleep(0.01)
			except Exception as e:
				prints("启动时遇到错误：" + str(e), "red")
				prints("请检查 IP 地址或更换端口。", "red")
				input("\033[0m")
				sys.exit(1)
			
			with open("./log.ndjson", "a", encoding="utf-8") as file:
				file.write(json.dumps({"type": "SERVER.START", "time": time_str(), "stamp": stamp, "version": VERSION, "config": config}) + "\n") # 协议 3.1
			
			side = "Server"
			prints("启动成功！", "green")
			# 响铃，显示帮助文本，显示聊天室各项信息，显示加入提示
			ring()
			do_help()
			do_dashboard()
			if config["gate"]["enter_hint"]:
				first_line = dye("[" + time_str()[11:19] + "]", "black")
				first_line += dye(" [您发送的]", "blue")
				first_line += " "
				first_line += dye(" [加入提示]", "red")
				first_line += " "
				first_line += dye("@", "black")
				first_line += dye(config["general"]["server_username"], "yellow")
				first_line += dye(":", "black")
				prints(first_line)
				prints(config["gate"]["enter_hint"], "white")
			
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
			# 当程序以客户端启动时，
			# 若 config.json 中加载到的 side 参数为 "Client"，
			# 则覆写为默认客户端配置
			if config["side"] == "Server" or config_read_result != "OK":
				config = DEFAULT_CLIENT_CONFIG
				config["username"] += time_str()[20:26]
				# 截取 "xxxx-xx-xx xx:xx:xx.xxxxxx" 中最后的 "xxxxxx"
				# 当作随机的用户名后缀，形成形如 "user123456" 的用户名
			tmp_ip = None
			if not auto_start:
				tmp_ip = input("\033[0m\033[1;37m服务端地址 [{}]：".format(config["ip"]))
			if not tmp_ip:
				tmp_ip = config["ip"]
			config["ip"] = tmp_ip
			tmp_port = None
			if not auto_start:
				tmp_port = input("\033[0m\033[1;37m端口 [{}]：".format(config["port"]))
			if not tmp_port:
				tmp_port = config["port"]
			try:
				tmp_port = int(tmp_port)
				if tmp_port < 1 or tmp_port > 65535:
					raise
			except:
				prints("参数错误：端口号应为不大于 65535 的正整数。", "red")
				input("\033[0m")
				sys.exit(1)
			config["port"] = tmp_port
			tmp_username = None
			if not auto_start:
				tmp_username = input("\033[0m\033[1;37m用户名 [{}]：".format(config["username"]))
			if not tmp_username:
				tmp_username = config["username"]
			config["username"] = tmp_username
			my_username = config["username"]
			# 同上，创建保存文件时使用的目录
			if platform.system() == "Windows":
				os.system("mkdir TouchFishFiles 1>nul 2>&1")
				os.system("mkdir TouchFishFiles\\{} 1>nul 2>&1".format(stamp))
			else:
				os.system("mkdir TouchFishFiles 1>/dev/null 2>&1")
				os.system("mkdir TouchFishFiles/{} 1>/dev/null 2>&1".format(stamp))
			try:
				with open("./config.json", "w", encoding="utf-8") as f:
					json.dump(config, f)
				prints("本次连接中输入的参数已经保存到配置文件 config.json，下次连接时将自动加载。", "yellow")
			except:
				prints("启动时遇到错误：配置文件 config.json 写入失败。", "red")
				input("\033[0m")
				sys.exit(1)
			try:
				with open("./log.ndjson", "a", encoding="utf-8") as f:
					pass
			except:
				prints("启动时遇到错误：无法向日志文件 log.ndjson 写入内容。", "red")
				input("\033[0m")
				sys.exit(1)
			
			my_socket = socket.socket()
			try:
				my_socket.connect((config["ip"], config["port"])) # 连接到服务端 socket
				# 同上，调整为非阻塞模式，缓冲区大小设置为 1 MiB，改善性能
				my_socket.setblocking(False)
				my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
				my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
				upload({"type": "GATE.REQUEST", "username": my_username}) # 协议 1.1
			except Exception as e:
				prints("启动时遇到错误：{}".format(e), "red")
				input("\033[0m")
				sys.exit(1)
			
			# 同上，设置 TCP 保活参数：启用功能，5 分钟后开始探测，间隔 30 秒
			if platform.system() == "Windows":
				my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
				my_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 300000, 30000))
			else:
				my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
				my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 300)
				my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
			
			with open("./log.ndjson", "a", encoding="utf-8") as file:
				file.write(json.dumps({"type": "SERVER.START", "time": time_str(), "stamp": stamp, "version": VERSION, "config": config}) + "\n") # 协议 3.1
			
			# 核验协议 1.2，获取加入请求结果
			try:
				message = None
				seconds_consumed = 0
				print(dye("正在连接聊天室... (已经等待了 {} / 10 秒)\r", "yellow").format(seconds_consumed), end="", flush=True)
				for i in range(10):
					# 设置 10 秒的「窗口期」，每秒验证一次
					# 与服务端「错峰」0.5 秒，期望第一次验证就成功（总用时 1 秒）
					time.sleep(1)
					seconds_consumed += 1
					print(dye("正在连接聊天室... (已经等待了 {} / 10 秒)\r", "yellow").format(seconds_consumed), end="", flush=True)
					try:
						read()
						message = get_message()
						if not message:
							raise
						break
					except:
						pass
				if not message:
					seconds_consumed += 1
					raise
				if not message["result"] in ["Accepted", "Pending review"] + list(RESULTS.keys()):
					raise
			except:
				print()
				if seconds_consumed == 11:
					prints("连接失败：连接超时。", "red")
				else:
					prints("连接失败：对方返回的内容不符合 TouchFish v4 协议。", "red")
				prints("对方似乎不是 v4 及以上的 TouchFish 服务端。", "red")
				if seconds_consumed == 11:
					prints("（也有可能是对方服务器端口被防火墙拦截，请联系服务器所有者确认，或检查本地网络及防火墙设置。）", "red")
				with open("./log.ndjson", "a", encoding="utf-8") as file:
					file.write(json.dumps({"type": "SERVER.STOP.LOG", "time": time_str()}) + "\n") # 协议 3.4.2
				input("\033[0m")
				sys.exit(1)
			
			if not message["result"] in ["Accepted", "Pending review"]:
				print()
				prints("连接失败：{}".format(RESULTS[message["result"]]), "red")
				with open("./log.ndjson", "a", encoding="utf-8") as file:
					file.write(json.dumps({"type": "SERVER.STOP.LOG", "time": time_str()}) + "\n") # 协议 3.4.2
				input("\033[0m")
				sys.exit(1)
			
			if message["result"] == "Accepted":
				print()
				prints("连接成功！", "green")
				ring()
			
			if message["result"] == "Pending review":
				print()
				seconds_consumed = 0
				while True:
					clock_start = datetime.datetime.now().timestamp()
					print(dye("服务端需要对连接请求进行人工审核，请等待... (已经等待了 {} 秒)\r", "white").format(seconds_consumed), end="", flush=True)
					try:
						read()
						message = get_message()
						if not message:
							raise
						# 特殊情况：聊天室服务端已经关闭 (协议 3.4.1)
						if message["type"] == "SERVER.STOP.ANNOUNCE":
							prints("聊天室服务端已经关闭。", "red")
							prints("连接失败。", "red")
							with open("./log.ndjson", "a", encoding="utf-8") as file:
								file.write(json.dumps({"type": "SERVER.STOP.LOG", "time": time_str()}) + "\n") # 协议 3.4.2
							input("\033[0m")
							sys.exit(1)
						# 一般情况：人工审核完成 (协议 1.3)
						if not message["accepted"]:
							print()
							prints("服务端管理员 {} (UID = {}) 拒绝了您的连接请求。".format(message["operator"]["username"], message["operator"]["uid"]), "red")
							prints("连接失败。", "red")
							with open("./log.ndjson", "a", encoding="utf-8") as file:
								file.write(json.dumps({"type": "SERVER.STOP.LOG", "time": time_str()}) + "\n") # 协议 3.4.2
							input("\033[0m")
							sys.exit(1)
						if message["accepted"]:
							time.sleep(1) # 等待 1 秒，确认协议 3.2 提供的完整上下文传输完成
							print()
							prints("服务端管理员 {} (UID = {}) 通过了您的连接请求。".format(message["operator"]["username"], message["operator"]["uid"]), "green")
							prints("连接成功！", "green")
							ring()
							break
					except SystemExit:
						sys.exit(1)
					except:
						pass
					clock_end = datetime.datetime.now().timestamp()
					seconds_consumed += 1
					time.sleep(max(1 - (clock_end - clock_start), 0))
			
			side = "Client"
			# 获取服务端通过协议 3.2 提供的完整上下文；
			# 此时自己应当处于 Online 状态
			read()
			first_data = get_message()
			server_version = first_data["server_version"]
			my_uid = first_data["uid"]
			config = first_data["config"]
			users = first_data["users"]
			# 自行计算在线人数（包括自己）
			online_count = 0
			for user in users:
				if user["status"] in ["Pending", "Online", "Admin", "Root"]:
					online_count += 1
			
			# 显示帮助文本，显示聊天室各项信息，显示加入提示
			do_help()
			do_dashboard()
			for i in first_data["chat_history"]:
				print_message(i)
				bell_countdown = 0 # 历史消息中的广播不需要额外响铃
			if config["gate"]["enter_hint"]:
				first_line = dye("[" + time_str()[11:19] + "]", "black")
				first_line += dye(" [加入提示]", "red")
				first_line += " "
				first_line += dye("@", "black")
				first_line += dye(config["general"]["server_username"], "yellow")
				first_line += dye(":", "black")
				prints(first_line)
				prints(config["gate"]["enter_hint"], "white")
			
			THREAD_INPUT = threading.Thread(target=thread_input)
			THREAD_OUTPUT = threading.Thread(target=thread_output)
			THREAD_LOG = threading.Thread(target=thread_log)
			
			THREAD_INPUT.start()
			THREAD_OUTPUT.start()
			THREAD_LOG.start()
	except BaseException as e:
		print()
		prints("程序运行时遇到错误：" + str(e), "red")
		print("\033[0m")

if __name__ == "__main__":
	main()





# End of program
