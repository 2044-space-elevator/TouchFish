import socket
import threading
import platform
import sys
import requests
import os
import json
import datetime
import base64
import readline  # 用于改善命令行输入体验

# 文件传输相关的常量
EXIT_FLG = False
FILE_START = "[FILE_START]"
FILE_DATA = "[FILE_DATA]"
FILE_END = "[FILE_END]"
CHUNK_SIZE = 8192

# 当前版本
CURRENT_VERSION = "v3.2.0"

def get_hh_mm_ss() -> str:
    """
    return HH:MM:SS
    like 11:45:14
    """
    return datetime.datetime.now().strftime("%H:%M:%S")

def clear_screen():
    """清屏"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_colored(text, color_code):
    """打印带颜色的文本"""
    print(f"\033[{color_code}m{text}\033[0m")

class ChatClientCLI:
    def __init__(self):
        self.socket = None
        self.username = ""
        self.server_ip = ""
        self.port = 0
        self.bell_enabled = False
        self.receiving_file = False
        self.current_file = {"name": "", "data": [], "size": 0}
        self.sending_file = None
        
        clear_screen()
        self.show_welcome()
        self.setup_connection()

    def show_welcome(self):
        """显示欢迎信息"""
        print_colored("=" * 50, "1;34")
        print_colored("   聊天室客户端 (命令行版本)", "1;34")
        print_colored("=" * 50, "1;34")
        print()
        
        try:
            newest_version = requests.get("https://www.bopid.cn/chat/newest_version_client.html", timeout=5).content.decode()
            version_info = f"当前版本: {CURRENT_VERSION}, 最新版本: {newest_version}"
            if newest_version != CURRENT_VERSION:
                print_colored(version_info + " (有新版本可用!)", "1;33")
            else:
                print_colored(version_info, "1;32")
        except:
            print_colored(f"当前版本: {CURRENT_VERSION} (无法检查更新)", "1;33")
        
        print()
        print_colored("命令说明:", "1;36")
        print_colored("  /help     - 显示帮助", "36")
        print_colored("  /file     - 发送文件", "36")
        print_colored("  /bell     - 切换提示音", "36")
        print_colored("  /clear    - 清屏", "36")
        print_colored("  /exit     - 退出聊天室", "36")
        print()
        print_colored("提示: 直接输入消息并按回车发送", "1;35")
        print()

    def setup_connection(self):
        """设置连接参数"""
        print_colored("连接设置", "1;33")
        print("-" * 30)
        
        self.server_ip = input("服务器 IP [127.0.0.1]: ").strip()
        if not self.server_ip:
            self.server_ip = "127.0.0.1"
            
        port_input = input("端口 [8080]: ").strip()
        self.port = int(port_input) if port_input else 8080
        
        while not self.username:
            self.username = input("用户名: ").strip()
            if not self.username:
                print_colored("用户名不能为空!", "1;31")
        
        self.connect_to_server()

    def connect_to_server(self):
        """连接到服务器"""
        try:
            print_colored(f"正在连接 {self.server_ip}:{self.port}...", "1;33")
            self.socket = socket.socket()
            self.socket.connect((self.server_ip, self.port))

            # 心跳包防止断连
            if platform.system() == "Windows":
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
                self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 180 * 1000, 30 * 1000))
            else:
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180 * 60)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)

            self.socket.send(bytes(f"用户 {self.username} 加入聊天室。\n", encoding="utf-8"))
            print_colored("连接成功!", "1;32")
            
            # 启动消息接收线程
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # 开始聊天界面
            self.chat_interface()
            
        except Exception as e:
            print_colored(f"连接失败: {str(e)}", "1;31")
            if input("是否重试? (y/n): ").lower() == 'y':
                self.setup_connection()
            else:
                sys.exit()

    def chat_interface(self):
        """聊天主界面"""
        clear_screen()
        print_colored(f"聊天室 - {self.username}", "1;34")
        print_colored("输入 /help 查看可用命令", "36")
        print("-" * 50)
        
        while True:
            try:
                message = input().strip()
                
                if not message:
                    continue
                    
                # 处理命令
                if message.startswith('/'):
                    self.handle_command(message)
                else:
                    # 发送普通消息
                    self.send_message(message)
                    
            except KeyboardInterrupt:
                self.cleanup_exit()
            except EOFError:
                self.cleanup_exit()

    def handle_command(self, command):
        """处理命令"""
        cmd = command.lower().split()[0]
        
        if cmd == '/help':
            self.show_help()
        elif cmd == '/file':
            self.send_file()
        elif cmd == '/bell':
            self.bell_enabled = not self.bell_enabled
            status = "开启" if self.bell_enabled else "关闭"
            print_colored(f"提示音已{status}", "1;32")
        elif cmd == '/clear':
            clear_screen()
            print_colored(f"聊天室 - {self.username}", "1;34")
            print_colored("输入 /help 查看可用命令", "36")
            print("-" * 50)
        elif cmd == '/exit':
            self.cleanup_exit()
        else:
            print_colored("未知命令，输入 /help 查看可用命令", "1;31")

    def show_help(self):
        """显示帮助信息"""
        print_colored("\n命令列表:", "1;36")
        print_colored("  /help     - 显示此帮助信息", "36")
        print_colored("  /file     - 发送文件", "36")
        print_colored("  /bell     - 切换提示音 (当前: " + 
                     ("开启" if self.bell_enabled else "关闭") + ")", "36")
        print_colored("  /clear    - 清屏", "36")
        print_colored("  /exit     - 退出聊天室", "36")
        print()

    def send_message(self, message):
        """发送消息"""
        full_msg = f"{self.username}: {message}\n"
        try:
            self.socket.send(full_msg.encode("utf-8"))
            # 在本地显示自己发送的消息
            print_colored(f"[{get_hh_mm_ss()}] {full_msg.strip()}", "1;30")
        except Exception as e:
            print_colored(f"发送失败: {str(e)}", "1;31")

    def receive_messages(self):
        """接收消息的线程函数"""
        buffer = b""
        while True:
            if EXIT_FLG:
                return
            try:
                chunk = self.socket.recv(1024)
                if not chunk:
                    continue

                buffer += chunk

                while b'\n' in buffer:
                    message_bytes_tmp, buffer_tmp = buffer.split(b'\n', 1)
                    message_tmp = message_bytes_tmp.decode('utf-8')

                    # 处理文件传输消息
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
                    
                    # 显示消息（自己发送的消息已经在send_message中显示）
                    if not message.startswith(f"{self.username}:"):
                        print_colored(f"[{get_hh_mm_ss()}] {message}", "1;37")
                        
                        # 播放提示音
                        if self.bell_enabled and not message.startswith(f"{self.username}:"):
                            self.play_notification_sound()

            except Exception as e:
                if not EXIT_FLG:
                    print_colored(f"接收消息错误: {str(e)}", "1;31")

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
        file_path = input("请输入文件路径: ").strip().strip('"')
        
        if not file_path or not os.path.exists(file_path):
            print_colored("文件不存在!", "1;31")
            return

        file_name = os.path.basename(file_path)
        self.sending_file = file_name
        
        print_colored(f"开始发送文件: {file_name}", "1;33")
        
        def send_file_thread():
            try:
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
                        print(f"\r发送进度: {progress:.1f}%", end="", flush=True)

                # 发送文件结束标记
                end_info = {
                    "type": FILE_END
                }
                self.socket.send(f"{json.dumps(end_info)}\n".encode("utf-8"))

                print_colored(f"\n文件 {file_name} 发送完成!", "1;32")
                self.sending_file = None

            except Exception as e:
                print_colored(f"\n文件发送失败: {str(e)}", "1;31")
                self.sending_file = None

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
                
                file_size_mb = msg_data["size"] / 1024 / 1024
                print_colored(f"\n收到文件传输请求: {msg_data['name']} ({file_size_mb:.1f}MB)", "1;33")
                response = input("是否接收? (y/n): ").lower()
                
                if response == 'y':
                    print_colored(f"开始接收文件: {msg_data['name']}", "1;32")
                else:
                    self.receiving_file = False
                    self.current_file = {"name": "", "data": [], "size": 0}
                    return True

            elif msg_data["type"] == FILE_DATA and self.receiving_file:
                self.current_file["data"].append(base64.b64decode(msg_data["data"]))
                received_size = sum(len(d) for d in self.current_file["data"])
                progress = (received_size / self.current_file["size"]) * 100
                print(f"\r接收进度: {progress:.1f}%", end="", flush=True)

            elif msg_data["type"] == FILE_END and self.receiving_file:
                if self.sending_file == self.current_file["name"]:
                    self.sending_file = None
                    return True

                # 保存文件
                default_name = self.current_file["name"]
                save_path = input(f"\n请输入保存路径 [./{default_name}]: ").strip()
                if not save_path:
                    save_path = f"./{default_name}"

                # 确保目录存在
                os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

                with open(save_path, "wb") as f:
                    for data in self.current_file["data"]:
                        f.write(data)
                        
                print_colored(f"文件已保存到: {save_path}", "1;32")
                self.receiving_file = False
                self.current_file = {"name": "", "data": [], "size": 0}

        except json.JSONDecodeError:
            return False
        except Exception as e:
            print_colored(f"文件接收出错: {str(e)}", "1;31")
            self.receiving_file = False
            self.current_file = {"name": "", "data": [], "size": 0}
            return False
        return True

    def cleanup_exit(self):
        """清理并退出"""
        global EXIT_FLG
        try:
            self.socket.send(f"用户 {self.username} 离开了聊天室。".encode("utf-8"))
            self.socket.close()
        except:
            pass
        EXIT_FLG = True
        print_colored("\n再见!", "1;34")
        sys.exit()

if __name__ == "__main__":
    try:
        ChatClientCLI()
    except KeyboardInterrupt:
        print_colored("\n程序已退出", "1;34")
        sys.exit()