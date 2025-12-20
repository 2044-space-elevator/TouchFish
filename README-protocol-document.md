# TouchFish v4 协议文档

本协议分为三个部分，`Gate`，`Chat` 和 `Server`，协议均使用 NDJSON（JSON 格式，相邻两个 JSON 以换行符分隔）格式进行发送。英文版和 JSON 代码块见 [protocol.txt](protocol.txt)。
**注：本文档内容大部分由AI生成，可能会有漏洞或错误，具体请阅读[protocol.txt](protocol.txt)**

本协议分为三个部分，`Gate`，`Chat` 和 `Server`，协议均使用 json 格式进行发送。英文版和 json 代码块见 [protocol.txt](protocol.txt)。

---

# 1. Gate

这个部分是关于进入聊天室的请求、审核等操作的协议内容。

## 1.1 Request

客户端连接时向服务端发送此消息，用于申请加入。

- `type`: `"GATE.REQUEST"`（所有协议的 `type` 字段均为固定值，下同）
- `username`: 字符串，表示用户希望使用的用户名。（所有 `username` 字段必须非空，下同）

## 1.2 Response

服务端对 `1.1 Request` 的直接响应，告知客户端其请求的处理结果。

- `type`: `"GATE.RESPONSE"`
- `result`: 字符串，可能取值包括：（下同）
  - `"Accepted"`：立即允许加入；
  - `"Pending review"`：需人工审核；
  - `"IP is banned"`：当前 IP 被封禁；
  - `"Room is full"`：服务端用户数已达上限；
  - `"Duplicate usernames"`：用户名已被使用；
  - `"Username consists of banned words"`：用户名包含违禁词。

## 1.3 Review Result

当请求状态为 `"Pending review"` 时，管理员审核完成后，服务端向该客户端发送此消息。

- `type`: `"GATE.REVIEW_RESULT"`
- `accepted`: 布尔值，`true` 表示通过，`false` 表示拒绝。
- `operator`: 审核者信息：
  - `username`: 操作者用户名；
  - `uid`: 操作者的用户 ID。（除特殊说明外，用户 ID 为非负整数，下同）

## 1.4 Incorrect Protocol

当出现通信不符合协议规范的连接时，服务端向日志写入记录。

- `type`: `"GATE.INCORRECT_PROTOCOL"`
- `time`: 表示事件发生的时间。（精确到微秒，下同）
- `ip`: 字符串，表示连接的网络地址。（格式为 `IPv4:port`，下同）

## 1.5 Client Request

服务端对客户端连接请求的响应。

### 1.5.1 Announce

服务端向所有已连接的客户端广播该客户端的连接请求。

- `type`: `"GATE.CLIENT_REQUEST.ANNOUNCE"`
- `username`: 用户名。
- `uid`: 服务端为该用户分配的用户 ID。
- `result`: 服务端对该请求的处理结果。

### 1.5.2 Log

服务端向接收到的连接请求写入日志。

- `type`: `"GATE.CLIENT_REQUEST.LOG"`
- `time`: 同上。
- `ip`: 客户端 IP 地址与端口。  
- `username`: 用户名。
- `uid`: 用户 ID。

## 1.6 Status Change

关于用户状态变更事件的协议。

### 1.6.1 Request

由管理员向服务端发起的用户状态变更请求。

- `type`: `"GATE.STATUS_CHANGE.REQUEST"`
- `status`: 字符串，表示目标状态，可能取值包括：（下同）
  - `"Rejected"`：连接被拒绝的用户；（本协议中表示管理员拒绝加入请求）
  - `"Kicked"`：被踢出聊天室的用户；（本协议中表示管理员主动踢出用户）
  - `"Offline"`：主动离开聊天室的用户；（本协议中不会出现）
  - `"Pending"`：等待加入审核的用户；（本协议中不会出现）
  - `"Online"`：在线用户；（本协议中表示管理员通过加入请求）
  - `"Admin"`：在线管理员；（本协议中不会出现）
  - `"Root"`：聊天室房主。（本协议中不会出现）
- `uid`: 被操作用户的用户 ID。

### 1.6.2 Announce

当用户状态变更时，服务端进行广播。

- `type`: `"GATE.STATUS_CHANGE.ANNOUNCE"` 
- `status`: 新状态。
- `uid`: 被变更状态的用户 ID。

### 1.6.3 Log

服务端将用户状态变更事件写入日志。

- `type`: 固定为 `"GATE.STATUS_CHANGE.LOG"`。  
- `time`: 同上。  
- `status`: 新状态。（`Pending` 状态和 `Root` 状态不会出现）  
- `uid`: 被操作用户的用户 ID。
- `operator`: 操作者的用户 ID。

---

# 2. Chat

这个部分是关于在聊天室内收发消息和文件的协议内容。

## 2.1 Send

客户端发送消息或文件。

- `type`: `"CHAT.SEND"`
- `filename`: 文件名。若发送的是普通文本消息，则为空字符串 `""`；若发送文件，则为原始文件名。（下同）
- `content`: 若为消息，则为原始文本内容；若为文件，则为文件内容的 Base64 编码字符串。（下同） 
- `to`: 目标接收者，可能取值包括：（下同）
  - `-2`：广播给所有在线用户（相较于普通发送有特殊提示）；  
  - `-1`：发送给所有在线用户；
  - 非负整数：私聊给拥有相应用户 ID 的用户。

## 2.2 Receive

服务端将消息转发给目标客户端。

- `type`: `"CHAT.RECEIVE"` 
- `from`: 发送者的用户 ID。（下同）
- `order`: 文件编号（用户区分不同的文件发送请求），可能取值包括：（下同）
  - `0`：普通文本消息；
  - 正整数：文件编号。
- `filename`: 同上。
- `content`: 同上。
- `to`: 同上。

## 2.3 Log

服务端将收到的聊天记录写入日志。

- `type`: `"CHAT.LOG"`
- `time`: 同上。
- `from`: 同上。
- `order`: 同上。 
- `filename`: 同上。
- `content`: 若为消息，则为原始文本内容；若为文件，则为空字符串 `""`。（为了防止日志文件过大，具体的文件内容会单独存储）
- `to`: 同上。

---

# 3. Server

这个部分是关于服务端运行情况的协议内容。

## 3.1 Start

服务端将启动时的启动参数写入日志。

- `type`: `"SERVER.START"`
- `time`: 同上。 
- `server_version`: 字符串，表示服务端程序版本。（下同） 
- `config`: JSON 对象，表示启动参数。（具体格式详见代码，下同）

## 3.2 Data

用于向新连接的客户端提供完整上下文。

- `type`: `"SERVER.DATA"`
- `server_version`: 同上。
- `uid`: 表示服务端分配给该用户的用户 ID。
- `config`: 同上。
- `users`: 用户列表，每个元素为：
  - `username`: 用户名；
  - `status`: 同上。 
- `chat_history`: 历史聊天记录，每条记录包含：（不包含私聊记录和文件发送记录）
  - `time`: 同上；
  - `from`: 同上；
  - `content`: 同上；
  - `to`: 同上。

## 3.3 Stop

服务端正常关闭时的协议。

### 3.3.1 Announce

服务端正常关闭时，向全体客户端进行广播。

- `type`: `"SERVER.STOP.ANNOUNCE"`

### 3.3.2 Log

服务端正常关闭时将事件写入日志。

- `type`: `"SERVER.STOP.LOG"`
- `time`: 同上。

## 3.4 Config

### 3.4.1 Post

管理员向服务端发送配置修改请求。

- `type`: `"SERVER.CONFIG.POST"`
- `key`: 配置项名称。（下同）
- `value`: 配置值。（下同）

### 3.4.2 Change

服务端向客户端广播配置修改事件。

- `type`: `"SERVER.CONFIG.CHANGE"`
- `key`: 同上。
- `value`: 同上。
- `operator`: 执行修改操作的用户 ID。

### 3.4.3 Save

服务端将聊天室房主导出配置的事件写入日志。

- `type`: `"SERVER.CONFIG.SAVE"`
- `time`: 同上。

### 3.4.4 Log

服务端将配置修改事件写入日志。

- `type`: `"SERVER.CONFIG.LOG"`
- `time`: 变更时间戳（微秒）。  
- `key`: 同上。
- `value`: 同上。
- `operator`: 执行修改操作的用户 ID。
