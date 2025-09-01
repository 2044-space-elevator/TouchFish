import tkinter as tk
import socket
import threading
import platform
import sys
import requests
from tkinter import messagebox
import datetime

def get_hh_mm_ss() -> str:
    """
    return HH:MM:SS
    like 11:45:14
    """
    return datetime.datetime.now().strftime("%H:%M:%S")

class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("聊天客户端")
        self.font_family = ("微软雅黑", 12)
        self.bell_enabled = False
        
        self.create_connection_window()
        self.root.mainloop()

    def create_connection_window(self):
        """创建连接窗口"""
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()
        
        # 服务器地址
        tk.Label(frame, text="服务器IP:").grid(row=0, column=0, sticky="w")
        self.ip_entry = tk.Entry(frame, width=20)
        self.ip_entry.grid(row=0, column=1, pady=5)
        self.ip_entry.insert(0, "127.0.0.1")
        
        # 端口
        tk.Label(frame, text="端口:").grid(row=1, column=0, sticky="w")
        self.port_entry = tk.Entry(frame, width=10)
        self.port_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.port_entry.insert(0, "8080")
        
        # 用户名
        tk.Label(frame, text="用户名:").grid(row=2, column=0, sticky="w")
        self.user_entry = tk.Entry(frame, width=20)
        self.user_entry.grid(row=2, column=1, pady=5)
        
        # 连接按钮
        connect_btn = tk.Button(frame, text="连接", command=self.connect_to_server)
        connect_btn.grid(row=3, columnspan=2, pady=10)
        
        # 提示
        tk.Label(frame, text="提示: Ctrl+Enter 发送消息").grid(row=4, columnspan=2)

        CURRENT_VERSION = "v1.1.2"
        try:
            NEWEST_VERSION = requests.get("https://www.bopid.cn/chat/newest_version_client.html").content.decode()
        except:
            NEWEST_VERSION = "UNKNOWN"
        tk.Label(frame, text=f"提示2：当前版本为 {CURRENT_VERSION}，最新版本为 {NEWEST_VERSION}").grid(row=5, columnspan=2)

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
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
            self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (
                1, 180 * 1000, 30 * 1000
            )) 
            self.root.destroy()  # 关闭连接窗口
            self.create_chat_window()  # 打开聊天窗口
            # 启动消息接收线程
            threading.Thread(target=self.receive_messages, daemon=True).start()
            # self.receive_messages()
            self.chat_win.mainloop()
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接到服务器:\n{str(e)}")

    def create_chat_window(self):
        """创建聊天窗口"""
        self.chat_win = tk.Tk()
        self.chat_win.title(f"聊天室 - {self.username}")
        self.chat_win.geometry(f"600x400")
        
        
        self.chat_win.minsize(width=350, height=280)
        
        # 0行：聊天记录框，权重为1，表示它会尽可能地扩展占据垂直空间
        self.chat_win.grid_rowconfigure(0, weight=1)
        # 1行：消息输入框和发送按钮区域，权重为0，表示它保持其内容所需的最小高度
        self.chat_win.grid_rowconfigure(1, weight=0)
        # 2行：设置按钮区域，权重为0，表示它保持其内容所需的最小高度
        self.chat_win.grid_rowconfigure(2, weight=0)
        # 0列：主列，权重为1，表示它会尽可能地扩展占据水平空间
        self.chat_win.grid_columnconfigure(0, weight=1)

        # 聊天记录框 (现在是一个Frame，包含Text和Scrollbar)
        self.chat_frame = tk.Frame(self.chat_win, bd=2, relief="sunken")
        
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5)) # 粘附到所有方向以填充单元格
        
        # 配置 chat_frame 内部的 grid 布局
        self.chat_frame.grid_rowconfigure(0, weight=1) # Text组件所在的行
        self.chat_frame.grid_columnconfigure(0, weight=1) # Text组件所在的列

        scrollbar = tk.Scrollbar(self.chat_frame)
        
        scrollbar.grid(row=0, column=1, sticky="ns") # 粘附到垂直方向

        self.chat_text = tk.Text(
            self.chat_frame, 
            yscrollcommand=scrollbar.set,
            font=self.font_family,
            state="disabled",
            wrap="word" # 确保文本自动换行
        )
        
        self.chat_text.grid(row=0, column=0, sticky="nsew") # 粘附到所有方向
        scrollbar.config(command=self.chat_text.yview)
        
        # 消息输入框 (现在是一个Frame，包含Text和Button)
        input_frame = tk.Frame(self.chat_win, bg="#e0e0e0")
        
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5) # 粘附到东西方向

        # 配置 input_frame 内部的 grid 布局
        input_frame.grid_columnconfigure(0, weight=1) # 消息输入框所在的列，会扩展
        input_frame.grid_columnconfigure(1, weight=0) # 发送按钮所在的列，保持最小宽度
        input_frame.grid_rowconfigure(0, weight=1) # 确保Text组件可以垂直扩展

        self.msg_entry = tk.Text(
            input_frame, 
            height=3,
            font=self.font_family,
            wrap="word" # 确保输入框文本也自动换行
        )
        
        self.msg_entry.grid(row=0, column=0, sticky="nsew", padx=(0, 5)) # 粘附到所有方向
        self.msg_entry.bind("<Control-Return>", lambda e: self.send_message())
        
        # 发送按钮
        send_btn = tk.Button(input_frame, text="发送", command=self.send_message)
        
        send_btn.grid(row=0, column=1, sticky="ew") # 粘附到东西方向
        
        # 设置按钮
        setting_btn = tk.Button(self.chat_win, text="设置", command=self.open_settings)
        
        setting_btn.grid(row=2, column=0, sticky="ew", pady=5) # 粘附到东西方向

        


    def open_settings(self):
        """打开设置窗口"""
        settings_win = tk.Toplevel(self.chat_win)
        settings_win.title("设置")
        settings_win.transient(self.chat_win)
        settings_win.grab_set()
        
        # 字体设置
        font_frame = tk.LabelFrame(settings_win, text="字体设置", padx=10, pady=10)
        font_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(font_frame, text="字体名称:").grid(row=0, column=0, sticky="w")
        font_name_entry = tk.Entry(font_frame)
        font_name_entry.grid(row=0, column=1, padx=5, pady=2)
        font_name_entry.insert(0, self.font_family[0])
        
        tk.Label(font_frame, text="字体大小:").grid(row=1, column=0, sticky="w")
        font_size_entry = tk.Entry(font_frame)
        font_size_entry.grid(row=1, column=1, padx=5, pady=2)
        font_size_entry.insert(0, str(self.font_family[1]))
        
        # 提示音设置
        bell_frame = tk.LabelFrame(settings_win, text="提示音设置", padx=10, pady=10)
        bell_frame.pack(padx=10, pady=5, fill="x")
        
        bell_var = tk.BooleanVar(value=self.bell_enabled)
        bell_check = tk.Checkbutton(
            bell_frame, 
            text="启用消息提示音",
            variable=bell_var,
            state="normal" if platform.system() == "Windows" else "disabled"
        )
        bell_check.pack(anchor="w")
        
        # 确定按钮
        def apply_settings():
            try:
                font_name = font_name_entry.get()
                font_size = int(font_size_entry.get())
                self.font_family = (font_name, font_size)
                
                self.bell_enabled = bell_var.get()
                
                self.chat_text.config(font=self.font_family)
                settings_win.destroy()
            except ValueError:
                messagebox.showerror("错误", "字体大小必须是整数")
        
        tk.Button(
            settings_win, 
            text="确定", 
            command=apply_settings
        ).pack(pady=10)

    def send_message(self):
        """发送消息"""
        message = self.msg_entry.get("1.0", "end").strip()
        if not message:
            return
            
        full_msg = f"{self.username}: {message}\n"
        try:
            self.socket.send(full_msg.encode("utf-8"))
            self.msg_entry.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("发送错误", f"消息发送失败:\n{str(e)}")

    def receive_messages(self):
        """接收消息的线程函数"""
        while True:
            try:
                message = self.socket.recv(1024).decode("utf-8")
                if not message:
                    continue
                message_show = f"[{get_hh_mm_ss()}] " + message
                
                    
                # 在GUI线程更新界面
                self.chat_win.after(0, self.display_message, message_show)
                
                # 播放提示音
                if self.bell_enabled and not message.startswith(f"{self.username}:"):
                    self.play_notification_sound()
                    
            except Exception as e:
                break

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

    def on_closing(self):
        """关闭窗口时的处理"""
        try:
            self.socket.close()
        except:
            pass
        self.chat_win.destroy()
        sys.exit()

if __name__ == "__main__":
    ChatClient()
