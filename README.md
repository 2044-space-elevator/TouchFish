> [!WARNING]
> **这是 TouchFish v4 版本，自 v4 开始不再向前兼容 v1 - v3。**

> **重要通知：贡献者须知**
>
> 感谢您对 TouchFish 项目的关注和贡献！为避免您的努力付诸东流，请在提交 PR 前务必仔细阅读
> **[贡献者指南](https://github.com/2044-space-elevator/TouchFish/blob/main/CONTRIBUTING.md)**，
> 确保您的贡献符合项目规范。感谢您的配合！

# TouchFish - 局域网聊天解决方案

## 目录

- [演示](#演示)
- [快速开始](#快速开始)
  - [作为服务端](#作为服务端)
  - [最为客户端](#作为客户端)
- [系统要求](#系统要求)
- [下载方式](#下载方式)
- [发行版本生态](#发行版本生态)

## 演示

请观看[此视频](https://www.bilibili.com/video/BV1qqSqB4E6x)以查看 v4 版本的用法。

该视频演示的程序为 beta 版本，与正式发行版有若干出入，敬请谅解。

## 相比于 v3 的变化

- 合并 Client 和 Server 为一个程序（`LTS.py`）
- 目前仅提供命令行（GUI 版本即将跟进）
- 更换协议（见源代码开头）

## 快速开始

### 作为服务端

1. **获取内网 IP 地址**：
   - **Windows**: 命令提示符执行 `ipconfig`，查找 "无线局域网适配器 WLAN" 下的 "IPv4 地址"
   - **Linux**: 终端执行 `ip a`

2. **检查端口可用性**：
   - **Windows**: `netstat -an | findstr <portid>`（无输出表示端口空闲）

3. **第一次启动服务器**：
   - 运行程序
   - 按下 `Enter`
   - 指定启动方式（`Server`）
   - 输入内网 IP 地址
   - 指定可用端口
   - 设置服务端昵称（将在聊天室中显示）
   - 设置最大用户数（不超过 128）
   - 将 IP 地址和端口信息分享给客户端用户

4. **后续启动服务器**：
   - 运行程序
   - 根据指示按下 `Ctrl + C` 或 `Ctrl + D`
   - 程序将自动以上次的配置启动

### 作为客户端

1. **第一次启动程序**：
   - 运行程序
   - 按下 `Enter`
   - 指定启动方式（`Client`）
   - 输入服务器 IP 地址
   - 输入服务器端口
   - 设置个人昵称（将在聊天室中显示）

2. **后续启动程序**：
   - 运行程序
   - 根据指示按下 `Ctrl + C` 或 `Ctrl + D`
   - 程序将自动以上次的配置启动

## 系统要求

### Windows

- **Windows 7 及以下系统用户**：可能需要安装额外的 DLL 文件
- 部分 Windows 版本可能不支持 ANSI 转义显示文字，建议使用 Windows 10 及以上系统
- 如果提示文件写入失败，请以管理员身份重新运行

### macOS

> [!WARNING]
> 需要启用 "任何来源" 应用运行权限：  
> 系统设置 → 安全性与隐私 → 安全性 → 允许以下来源的应用程序 → 选择 "任何来源"

### Linux

无特殊限制，服务端部署**不建议**使用编译后的二进制，更推荐使用源代码。

## 下载方式

### 推荐镜像站点

**镜像站**: [https://mirror.ilovescratch.us.ci/](https://mirror.ilovescratch.us.ci/)

> **优势**: 下载速度快，网络连接稳定
>
> **限制**: 仅提供稳定版本，无法下载 PR 分支和开发中版本

### 官方源

**GitHub**: [https://github.com/2044-space-elevator/TouchFish](https://github.com/2044-space-elevator/TouchFish)

> **优势**: 包含所有分支、PR 和最新开发版本
>
> **限制**: 国内访问可能较慢

---

以上是软件使用方法，以下是与软件生态等相关内容

---

## 发行版本生态

TouchFish 拥有丰富的衍生版本生态系统，满足不同用户需求：

**这里的大部分发行版都暂不支持 v4 版本，如需使用请前往 [Release](https://github.com/2044-space-elevator/TouchFish/releases) 页面下载旧版本（v3及以前）**

| 版本名称 | 简称 | 主要作者 | 链接 | 对 v1-3 支持 | 语言 | 平台支持 | 特色 | 对 v4 支持
|---------|------|----------|----|-----|------|----------|------|--|
| LTS | TF | @2044-space-elevator, @035966-L3 和其他 LTS 贡献者 | [github](#发行版本生态), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/LTS/) | ✅ | Python | Win, macOS, Linux | 根版本，长期支持 | ✅ |
| Astra | TFA | @ILoveScratch2 | [github](https://github.com/ILoveScratch2/TouchFish-Astra), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/Astra/) | ✅ | Dart | 全平台 (UI) | 最佳发行版之一，现代化 UI | ✅ |
| UI Remake | TFUR | @pztsdy | [github](https://github.com/pztsdy/touchfish_ui_remake), [main-mirror](https://mirror.ilovescratch.us.ci/TouchFish/UI%20Remake/), [update-branch](https://github.com/pztsdy/touchfish_ui_remake/tree/update) | ✅ | Node.JS | Win, macOS*, Linux* | 现代化 UI，Markdown，代码高亮（生命周期已终止~~即停更~~） | ❌ |
| Plus | Plus | @ayf2192538031 | [github](https://github.com/2044-space-elevator/TouchFishPlus), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/Plus%20(%E6%BA%90%E4%BB%A3%E7%A0%81)/) | ❌ | Python | Win*, macOS*, Linux* | 增强功能集 | ❌ |
| Pro | Pro | @BoXueDuoCai | [github](https://github.com/PigeonTechGroup/TouchFishPro), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/Pro%20(%E6%BA%90%E4%BB%A3%E7%A0%81)/) | ✅ | Python | Win*, macOS*, Linux* | Markdown，LaTeX，用户高亮 | ❌ |
| Android | (已废除) | @pztsdy | [github](https://github.com/pztsdy/TouchFish-for-mobile), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/Mobile%20%EF%BC%88%E4%B8%8D%E6%8E%A8%E8%8D%90%EF%BC%89/) | ✅ | Kotlin | Android | 移动端（有使用限制）（已停更） | ❌ |
| More | More | @xie2870 | [github](https://github.com/xie2870/touchfish_more), [gitee](https://gitee.com/xx2870/touchfish_more), [mirror](https://mirror.ilovescratch.us.ci/TouchFish/More(Lite)/) | ✅ | Python | Win*, macOS*, Linux (UI) | 性能优化，镜像站 | ❌ |

> *注：*  
> 标 * 的版本可能需要自行编译、直接运行代码或缺少预编译包  

---

> 特别感谢 @xie2870 对 v4 开发的间接指导。（~~实则是 v4 规划时将 More 的所有拓展功能均纳入了规划~~）