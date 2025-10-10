import tkinter as tk
from tkinter import ttk
import socket
import threading
import platform
import sys
import requests
import os
import json
from tkinter import messagebox, filedialog
import datetime
import win10toast
import base64
import webbrowser
from ctypes import windll

# 文件传输相关的常量
EXIT_FLG = False
FILE_START = "[FILE_START]"
FILE_DATA = "[FILE_DATA]"
FILE_END = "[FILE_END]"
CHUNK_SIZE = 8192
NOTIFIER_INIT_ERR = False

# 当前版本
CURRENT_VERSION = "v3.2.0"

notifier = None
if platform.system() == "Windows":
    try:
        notifier = win10toast.ToastNotifier()
    except Exception as e:
        NOTIFIER_INIT_ERR = True

def get_hh_mm_ss() -> str:
    """
    return HH:MM:SS
    like 11:45:14
    """
    return datetime.datetime.now().strftime("%H:%M:%S")

class ChatClient:
    def __init__(self):
        try:
            windll.shcore.SetProcessDpiAwareness(1)  # 或者使用 2 为 PerMonitorV2
        except:
            print("DPI 设置失败。")
            pass

        self.root = tk.Tk()
        self.root.title("聊天客户端")
        self.font_family = ("微软雅黑", 12)
        self.bell_enabled = False
        self.notifier_enabled = False
        self.notifier_str = []
        self.sending_file = None  # 添加标志来跟踪正在发送的文件

        self.create_connection_window()
        self.root.mainloop()

    def create_connection_window(self):
        """创建连接窗口"""
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()

        # 服务器地址
        tk.Label(frame, text="服务器 IP：").grid(row=0, column=0, sticky="w")
        self.ip_entry = tk.Entry(frame, width=20)
        self.ip_entry.grid(row=0, column=1, pady=5)
        self.ip_entry.insert(0, "127.0.0.1")

        # 端口
        tk.Label(frame, text="端口：").grid(row=1, column=0, sticky="w")
        self.port_entry = tk.Entry(frame, width=10)
        self.port_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.port_entry.insert(0, "8080")

        # 用户名
        tk.Label(frame, text="用户名：").grid(row=2, column=0, sticky="w")
        self.user_entry = tk.Entry(frame, width=20)
        self.user_entry.grid(row=2, column=1, pady=5)

        # 连接按钮
        connect_btn = tk.Button(frame, text="连接", command=self.connect_to_server)
        connect_btn.grid(row=3, columnspan=2, pady=10)

        # 提示
        tk.Label(frame, text="提示: Ctrl+Enter 发送消息").grid(row=4, columnspan=2)

        try:
            NEWEST_VERSION = requests.get("https://www.bopid.cn/chat/newest_version_client.html").content.decode()
        except:
            NEWEST_VERSION = "UNKNOWN"
        tk.Label(frame, text=f"提示 2：当前版本为 {CURRENT_VERSION}，最新版本为 {NEWEST_VERSION}").grid(row=5, columnspan=2)

        if NOTIFIER_INIT_ERR:
            messagebox.showwarning("警告", "Windows 通知功能初始化失败，无法显示通知。你是否在使用Win10以下的系统?")

    def connect_to_server(self):
        """连接到服务器"""
        try:
            self.server_ip = self.ip_entry.get()
            self.port = int(self.port_entry.get())
            self.username = self.user_entry.get()
            if not self.username:
                messagebox.showerror("错误", "用户名不能为空")
                return

            self.socket = socket.socket()
            self.socket.connect((self.server_ip, self.port))

            # 心跳包防止断连
            if platform.system() == "Windows":
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
                self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (
                    1, 180 * 1000, 30 * 1000
                )) 

            else:
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180 * 60)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)

            self.socket.send(bytes(f"用户 {self.username} 加入聊天室。\n", encoding="utf-8"))
            self.root.destroy()  # 关闭连接窗口
            self.create_chat_window()  # 打开聊天窗口
            # 启动消息接收线程
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.chat_win.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.chat_win.mainloop()
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接到服务器：\n{str(e)}")

    def create_chat_window(self):
        """创建聊天窗口"""
        self.chat_win = tk.Tk()
        self.chat_win.title(f"聊天室 - {self.username}")
        self.chat_win.geometry(f"1495x1130")

        # 聊天记录框
        self.chat_frame = tk.Frame(self.chat_win)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.chat_frame)
        scrollbar.pack(side="right", fill="y")

        self.chat_text = tk.Text(
            self.chat_frame, 
            yscrollcommand=scrollbar.set,
            font=self.font_family,
            state="disabled"
        )
        self.chat_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.chat_text.yview)

        # 消息输入框
        input_frame = tk.Frame(self.chat_win)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.msg_entry = tk.Text(
            input_frame, 
            height=3,
            font=self.font_family
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.msg_entry.bind("<Control-Return>", lambda e: self.send_message())

        # 发送按钮和文件按钮
        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(side="right")

        send_btn = tk.Button(btn_frame, text="发送", command=self.send_message)
        send_btn.pack(side="right", padx=2)

        file_btn = tk.Button(btn_frame, text="发送文件", command=self.send_file)
        file_btn.pack(side="right", padx=2)

        # 设置按钮
        setting_btn = tk.Button(self.chat_win, text="设置", command=self.open_settings)
        setting_btn.pack(side="bottom", pady=5)

        # 初始化文件传输相关的变量
        self.receiving_file = False
        self.current_file = {"name": "", "data": [], "size": 0}


    def open_settings(self):
        """打开设置窗口"""
        settings_win = tk.Toplevel(self.chat_win)
        settings_win.title("设置")
        settings_win.transient(self.chat_win)
        settings_win.grab_set()

        # 字体设置
        font_frame = tk.LabelFrame(settings_win, text="字体设置", padx=10, pady=10)
        font_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(font_frame, text="字体名称：").grid(row=0, column=0, sticky="w")
        font_name_entry = tk.Entry(font_frame)
        font_name_entry.grid(row=0, column=1, padx=5, pady=2)
        font_name_entry.insert(0, self.font_family[0])

        tk.Label(font_frame, text="字体大小：").grid(row=1, column=0, sticky="w")
        font_size_entry = tk.Entry(font_frame)
        font_size_entry.grid(row=1, column=1, padx=5, pady=2)
        font_size_entry.insert(0, str(self.font_family[1]))

        # 提示音设置
        bell_frame = tk.LabelFrame(settings_win, text="提示设置", padx=10, pady=10)
        bell_frame.pack(padx=10, pady=5, fill="x")

        bell_var = tk.BooleanVar(value=self.bell_enabled)
        bell_check = tk.Checkbutton(
            bell_frame, 
            text="启用消息提示音",
            variable=bell_var,
            state="normal" if platform.system() == "Windows" else "disabled"
        )
        bell_check.pack(anchor="w")
        notifier_var = tk.BooleanVar(value=self.notifier_enabled)
        notifier_check = tk.Checkbutton(
            bell_frame,
            text="启用 Windows 通知（无声音，仅限 Windows 系统）",
            variable=notifier_var,
            state="normal" if platform.system() == "Windows" else "disabled"
        )
        notifier_str_label = tk.Label(
            bell_frame,
            text="当收到这些字段时才启用通知（英文半角逗号分割，无内容表示收到任意字段都通知）："
        )
        notifier_str_entry = tk.Entry(
            bell_frame
        )
        notifier_check.pack(anchor="w")
        notifier_str_label.pack(anchor="w")
        notifier_str_entry.pack(anchor="w")
        notifier_str_entry.insert(0, ",".join(self.notifier_str))


        # 确定按钮和帮助按钮
        button_frame = tk.Frame(settings_win)
        button_frame.pack(pady=10)

        def apply_settings():
            try:
                font_name = font_name_entry.get()
                font_size = int(font_size_entry.get())
                self.font_family = (font_name, font_size)

                self.bell_enabled = bell_var.get()
                self.notifier_enabled = notifier_var.get()
                self.notifier_str = notifier_str_entry.get().split(',')

                self.chat_text.config(font=self.font_family)
                settings_win.destroy()
            except ValueError:
                messagebox.showerror("错误", "字体大小必须是整数")

        def open_help():
            webbrowser.open("https://touchfish-dev.notion.site/TouchFish-101-26781a521173808ebccfcb116d0f9075")

        tk.Button(
            button_frame, 
            text="确定", 
            command=apply_settings
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="帮助",
            command=open_help
        ).pack(side="left", padx=5)

    def send_message(self):
        """发送消息"""
        message = self.msg_entry.get("1.0", "end-1c") # 使用 end-1c 获取不带末尾换行符的内容
        while message.startswith("\n"):
            message = message[1:]
        if not message.strip():
            return
        full_msg = f"{self.username}: {message}\n"
        try:
            self.socket.send(full_msg.encode("utf-8"))
            self.msg_entry.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("发送错误", f"消息发送失败：\n{str(e)}")

    def receive_messages(self):
        """接收消息的线程函数"""
        buffer = b""
        while True:
            time.sleep(0.1)
            if EXIT_FLG:
                sys.exit()
                return
            try:
                # 接收原始字节数据
                chunk = self.socket.recv(1024)
                if not chunk:
                    continue

                buffer += chunk

                # 使用 b'\n' 作为分隔符处理消息
                while b'\n' in buffer:
                    message_bytes_tmp, buffer_tmp = buffer.split(b'\n', 1)
                    message_tmp = message_bytes_tmp.decode('utf-8')

                    # 尝试处理文件传输消息
                    if message_tmp.startswith("{") and message_tmp.endswith("}"):
                        if self.handle_file_message(message_tmp):
                            buffer = buffer_tmp
                            continue

                    # 处理普通文本消息
                    message_bytes = buffer
                    while message_bytes.endswith(b'\n'):
                        message_bytes = message_bytes[:-1]
                    buffer = b""
                    message = message_bytes.decode('utf-8')
                    if self.notifier_enabled and not message.startswith(f"{self.username}:"):
                        def notif_tmp():
                            title = ""
                            if message.startswith("[房主提示]"):
                                title = "房主提示"
                            elif message.startswith("[系统提示]"):
                                title = "系统提示"
                            elif message.startswith("[房主广播]"):
                                title = "房主广播"
                            else:
                                username = message.split(":")[0]
                                title = f"消息提示（来自 {username}）"
                            if notifier:  # 检查notifier是否存在
                                notifier.show_toast(title, message, duration=2)
                        if self.notifier_str:
                            for v in self.notifier_str:
                                if v in message:
                                    threading.Thread(target=notif_tmp).start()
                                    break
                        else:
                            threading.Thread(target=notif_tmp).start()

                    message_show = f"[{get_hh_mm_ss()}] " + message

                    # 在GUI线程更新界面
                    self.chat_win.after(0, self.display_message, message_show + "\n")

                    # 播放提示音
                    if self.bell_enabled and not message.startswith(f"{self.username}:"):
                        self.play_notification_sound()

            except Exception as e:
                # 打印异常信息以便调试
                print(f"Error in receive_messages: {e}")
                pass


    def display_message(self, message):
        """在聊天框中显示消息"""
        self.chat_text.config(state="normal")
        self.chat_text.insert("end", message)
        self.chat_text.see("end")
        self.chat_text.config(state="disabled")

    def play_notification_sound(self):
        """播放提示音（跨平台）"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(1000, 200)
            elif platform.system() == "Darwin":  # macOS
                import os
                os.system("afplay /System/Library/Sounds/Ping.aiff&")
            else:  # Linux
                import os
                os.system("paplay /usr/share/sounds/freedesktop/stereo/message.oga&")
        except:
            pass

    def send_file(self):
        """发送文件"""
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        self.sending_file = file_name

        # 创建进度条窗口
        progress_win = tk.Toplevel(self.chat_win)
        progress_win.title("文件发送进度")
        progress_win.geometry("300x150")
        progress_win.transient(self.chat_win)

        progress_label = tk.Label(progress_win, text="准备发送文件...")
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_win,
            variable=progress_var,
            maximum=100
        )
        progress_bar.pack(fill="x", padx=20, pady=10)

        def send_file_thread():
            try:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)

                # 发送文件开始标记
                start_info = {
                    "type": FILE_START,
                    "name": file_name,
                    "size": file_size
                }
                self.socket.send(f"{json.dumps(start_info)}\n".encode("utf-8"))

                # 读取并发送文件内容
                sent_size = 0
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break

                        # base64编码
                        chunk_b64 = base64.b64encode(chunk).decode("utf-8")

                        # 发送数据块
                        data_info = {
                            "type": FILE_DATA,
                            "data": chunk_b64
                        }
                        self.socket.send(f"{json.dumps(data_info)}\n".encode("utf-8"))

                        # 更新进度
                        sent_size += len(chunk)
                        progress = (sent_size / file_size) * 100
                        progress_win.after(0, lambda: progress_var.set(progress))
                        progress_win.after(0, lambda: progress_label.config(
                            text=f"发送进度：{progress:.1f}%"
                        ))

                # 发送文件结束标记
                end_info = {
                    "type": FILE_END
                }
                self.socket.send(f"{json.dumps(end_info)}\n".encode("utf-8"))

                progress_win.after(0, lambda: progress_label.config(text="文件发送完成！"))
                progress_win.after(1000, progress_win.destroy)

            except Exception as e:
                messagebox.showerror("发送错误", f"文件发送失败：\n{str(e)}")
                progress_win.destroy()

        # 在新线程中发送文件
        threading.Thread(target=send_file_thread).start()

    def handle_file_message(self, message):
        """处理文件传输相关的消息"""
        try:
            msg_data = json.loads(message)

            if msg_data["type"] == FILE_START:
                # 检查是否是自己正在发送的文件
                if self.sending_file == msg_data["name"]:
                    return True

                self.receiving_file = True
                self.current_file = {
                    "name": msg_data["name"],
                    "data": [],
                    "size": msg_data["size"]
                }
                # 询问用户是否接收文件
                if messagebox.askyesno("文件接收", 
                    f"是否接收文件：{msg_data['name']} ({msg_data['size'] / 1024 / 1024:.1f}MB)？"):
                    self.display_message(f"[系统提示] 开始接收文件：{msg_data['name']}\n")
                else:
                    self.receiving_file = False
                    self.current_file = {"name": "", "data": [], "size": 0}

            elif msg_data["type"] == FILE_DATA and self.receiving_file:
                self.current_file["data"].append(base64.b64decode(msg_data["data"]))
                received_size = sum(len(d) for d in self.current_file["data"])
                progress = (received_size / self.current_file["size"]) * 100
                # 在GUI线程更新进度
                self.chat_win.after(0, self.update_file_progress, progress)

            elif msg_data["type"] == FILE_END and self.receiving_file:
                if self.sending_file == self.current_file["name"]:
                    self.sending_file = None
                    return True

                # 保存文件
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".*",
                    initialfile=self.current_file["name"]
                )
                if save_path:
                    with open(save_path, "wb") as f:
                        for data in self.current_file["data"]:
                            f.write(data)
                    self.display_message(f"[系统提示] 文件已保存到：{save_path}\n")

                self.receiving_file = False
                self.current_file = {"name": "", "data": [], "size": 0}

        except json.JSONDecodeError:
            return False
        except Exception as e:
            self.display_message(f"[系统提示] 文件接收出错：{str(e)}\n")
            self.receiving_file = False
            self.current_file = {"name": "", "data": [], "size": 0}
            return False
        return True

    def update_file_progress(self, progress):
        """更新文件接收进度"""
        self.chat_text.config(state="normal")
        # 删除上一行进度提示
        self.chat_text.delete("end-2l", "end-1l")
        self.display_message(f"[系统提示] 文件接收进度：{progress:.1f}%\n")

    def on_closing(self):
        global EXIT_FLG
        """关闭窗口时的处理"""
        try:
            self.socket.send(f"用户 {self.username} 离开了聊天室。".encode("utf-8"))
            self.socket.close()
        except:
            pass
        EXIT_FLG = True
        self.chat_win.destroy()
        sys.exit()

if __name__ == "__main__":
    ChatClient()
