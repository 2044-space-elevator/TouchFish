> **本版本为兼容版本，指所有不同版本的 chat 和 client 不会出现连接问题。发信息功能可能出现兼容性问题，可以通过操作规避，详见 wiki。**

> [好看版链接](https://github.com/pztsdy/touchfish_ui_remake)，此版本基于 NodeJS 构建，拥有现代的 UI，支持 Markdown、代码高亮和洛谷 Markdown 编辑器，部分支持 $\LaTeX$。

> [进阶版本链接](https://github.com/2044-space-elevator/TouchFishPlus)，进阶版本有更多功能，对应地，不同发行版的 chat 和 client 可能出现极大的兼容性问题。

> **交 PR 的人注意！感谢您对 TouchFish 的贡献，但为了防止您的努力打水漂，请先阅读[贡献者须知](https://github.com/2044-space-elevator/TouchFish/blob/main/CONTRIBUTING.md)再开始贡献，感谢配合！**

# 机房聊天软件（断公网可用）

汪氏军工制作，Luogu UID:824363

孙大佬的网站，bopid.cn

该软件没什么优点（小声），只能发文字，只能在同一局域网下使用，显然很辣鸡，但是可以离线使用。所以是机房聊天的不二之选（doge）。

（小声）如果挂到服务器上，理论上可以在公网上使用。

该体系有两个软件：
- server。服务器端，聊天前，必须有一人的电脑作为 server，server 有且只有一台。
- client。客户端，聊天者都使用 client 程序。

## macos 用户注意

该软件需要打开任意来源以正常运行。

系统设置 – 安全性与隐私 – 安全性 – 允许一下来源的应用程序 – 点击 App Store 与已知开发者选项，然后选择 任何来源。

## server 的使用

server 需查询自己的内网 IP，打开 cmd，输入 ipconfig，找到“无线局域网适配器 WLAN:”中的“IPv4 地址”一项。自家的路由器应该是 "192.168.x.y"，学校的可能不一样。还有适配端口，适配端口通过 `netstat -an | findstr 要用的端口` 这一项命令来寻找，如果没有返回，就说明该端口空闲。

如果你使用 Linux，可以使用命令
```bash
ip a
```
来查看自己的内网 IP 地址，**即使你用的服务器，也请用内网 IP 地址**。

接着，查询到的 IP 地址复制，打开 server，粘贴自己的 IP，回车。之后要求你输入最大用户数，这个看有多少连接（一定是正整数）。然后输入之前试出来的端口。将你的 IP 地址和端口分享给 Client 端的成员（一台机子在一个网内的 IP 是基本恒相等的，端口的空闲与否基本不会改变，分享一次就够了）。

server 目前的命令行多元控制功能的使用，详见 wiki，或在命令行输入 `help`

## client 的使用

Client 是窗口版的，IP 输入 server 的 ip, username 输入自己的昵称（聊天室里显示的就是 username），port 输入 server 的端口。输入在下面的文本框输入，点击确认就可以发送。

## admin 的使用

admin 是控制台窗口，需要输入服务器开放的控制口，即可使用。

在 server 输入 `admin on` 开启控制口，输入 `admin add` 添加管理员。

admin 如何使用，详见 wiki。
