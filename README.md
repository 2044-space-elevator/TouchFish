# TouchFish - 局域网聊天解决方案

> [!INFO]
> **重要通知：贡献者须知**
> 
> 感谢您对 TouchFish 项目的关注和贡献！为避免您的努力付诸东流，请在提交 PR 前务必仔细阅读
> **[贡献者指南](https://github.com/2044-space-elevator/TouchFish/blob/main/CONTRIBUTING.md)**，
> 确保您的贡献符合项目规范。感谢您的配合！

**汪氏军工制作 | 作者 Luogu UID: 824363**

## 项目简介

TouchFish 是一款专为局域网环境设计的聊天软件，支持文字和图片传输。即使在没有公网连接的情况下，也能提供稳定的通信服务，是机房、实验室等封闭网络环境的理想选择。

> **项目官网**: [bopid.cn](https://www.bopid.cn/chat)

## 下载方式

### 推荐镜像站点
**镜像站**: [https://mirror.ilovescratch.dpdns.org/](https://mirror.ilovescratch.dpdns.org/)

> **优势**: 下载速度快，网络连接稳定
> 
> **限制**: 仅提供稳定版本，无法下载 PR 分支和开发中版本

### 官方源
**GitHub**: [https://github.com/2044-space-elevator/TouchFish](https://github.com/2044-space-elevator/TouchFish)

> **优势**: 包含所有分支、PR 和最新开发版本
> 
> **限制**: 国内访问可能较慢

## 系统要求

### Windows
- **Windows 7 及以下系统用户**: 可能需要安装额外的 DLL 文件

### macOS
> [!WARNING]
> 需要启用"任何来源"应用运行权限：
> 系统设置 → 安全性与隐私 → 安全性 → 允许以下来源的应用程序 → 选择"任何来源"

### Linux
> [!WARNING]
> 仅支持带有图形界面的 Linux 发行版。
> 无界面用户请使用 [CLI 版本](clientcli.py)

## 软件架构

TouchFish 采用客户端-服务器架构，包含三个核心组件：

- **Server（服务器端）**: 聊天网络的核心，同一网络内只需运行一个实例
- **Client（客户端）**: 普通用户聊天界面
- **Admin（管理员端）**: 授予信任用户的管理权限

## 发行版本生态

TouchFish 拥有丰富的衍生版本生态系统，满足不同用户需求：

| 版本名称 | 简称 | 主要作者 | 兼容性 | 语言 | 平台支持 | 特色 |
|---------|------|----------|--------|------|----------|------|
| LTS | TF | @2044-space-elevator | 是 | Python | Win, macOS, Linux(UI) | 根版本，长期支持 |
| CLI | cli | @JohnChiao75 | 是 | Python | Win, macOS, Linux | 命令行界面 |
| UI Remake | TFUR | @pztsdy | 是 | Node.JS | Win, macOS*, Linux* | 现代化 UI，Markdown，代码高亮 |
| Plus | Plus | @ayf2192538031 | 否 | Python | Win*, macOS*, Linux* | 增强功能集 |
| Pro | Pro | @BoXueDuoCai | 是 | Python | Win*, macOS*, Linux* | Markdown，LaTeX，用户高亮 |
| Android | mobile | @pztsdy | 是 | Kotlin | Android | 移动端（有使用限制） |
| Astra | - | @ILoveScratch2 | 是 | Dart | 全平台(UI) | 最佳发行版之一，现代化UI |
| More | More | @xx2860 | 是 | Python | Win*, macOS*, Linux(UI) | 性能优化，镜像站 |

> *注：标注星号的版本可能需要自行编译或缺少预编译包*

### 相关项目推荐

**Cloud Studio Chat** by @pztsdy: [项目链接](https://github.com/pztsdy/Cloud-Studio-Chat)  
基于 C++ 开发，具有优异的性能和兼容性，支持 32 位 XP 系统，提供与 TouchFish 相似的功能体验。

## 快速开始

### 服务器端配置

1. **获取内网 IP 地址**：
   - **Windows**: 命令提示符执行 `ipconfig`，查找"无线局域网适配器 WLAN"下的"IPv4 地址"
   - **Linux**: 终端执行 `ip a`

2. **检查端口可用性**：
   - **Windows**: `netstat -an | findstr 端口号`（无输出表示端口空闲）

3. **启动服务器**：
   - 运行 server 程序
   - 输入内网 IP 地址
   - 设置最大用户数（正整数）
   - 指定可用端口
   - 将 IP 地址和端口信息分享给客户端用户

> 详细的多控制功能请参阅 Wiki 或在命令行输入 `help`

### 客户端使用

1. 启动 Client 程序
2. 输入服务器 IP 地址
3. 设置个人昵称（将在聊天室中显示）
4. 输入服务器端口
5. 在文本框中输入消息，点击确认发送

### 管理员功能

通过控制台窗口连接服务器开放的控制端口，支持大部分服务器管理功能。详细使用方法请参阅 Wiki。

在服务器端使用 `admin on` 开启控制口，`admin add` 添加管理员。