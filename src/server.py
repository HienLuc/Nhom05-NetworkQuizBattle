import socket
import threading
import json

# Cấu hình Server
HOST = '127.0.0.1'
PORT = 65432

class QuizServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        
        # Danh sách quản lý kết nối
        # Format: {client_socket: {"addr": address, "name": "Username"}}
        self.clients = {} 
        
        print(f" Server đang chạy tại {HOST}:{PORT}")
        print("Waiting for connections...")

    def broadcast(self, message_dict, exclude_socket=None):
        """Gửi tin nhắn JSON cho tất cả client"""
        # Chuyển Dict -> JSON String -> Bytes
        try:
            msg_bytes = json.dumps(message_dict).encode('utf-8')
        except Exception as e:
            print(f" Error encoding JSON: {e}")
            return

        # Duyệt qua danh sách và gửi
        # Cần convert keys sang list để tránh lỗi "dictionary changed size during iteration"
        for client_sock in list(self.clients.keys()):
            if client_sock != exclude_socket:
                try:
                    client_sock.send(msg_bytes)
                except Exception as e:
                    print(f" Lỗi gửi tin cho {self.clients[client_sock]['addr']}: {e}")
                    self.remove_client(client_sock)

    def remove_client(self, client_socket):
        """Xử lý khi client ngắt kết nối"""
        if client_socket in self.clients:
            info = self.clients[client_socket]
            print(f" Client {info['name']} ({info['addr']}) đã thoát.")
            del self.clients[client_socket]
            client_socket.close()
            
            # Thông báo cho các người chơi khác (Optional)
            self.broadcast({
                "type": "INFO",
                "message": f"Người chơi {info['name']} đã rời phòng."
            })

    def handle_client(self, client_socket, addr):
        """Hàm xử lý logic cho từng luồng Client riêng biệt"""
        print(f" Kết nối mới từ: {addr}")
        
        # Mặc định chưa có tên
        self.clients[client_socket] = {"addr": addr, "name": "Unknown"}

        try:
            while True:
                # 1. Nhận dữ liệu (Buffer size 1024 bytes)
                data = client_socket.recv(1024)
                if not data:
                    break # Client đóng kết nối

                # 2. Giải mã dữ liệu (Bytes -> JSON)
                try:
                    msg_obj = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    print(f"⚠️ Nhận dữ liệu rác từ {addr}")
                    continue

                # 3. Xử lý các loại tin nhắn (Routing)
                msg_type = msg_obj.get("type")
                
                if msg_type == "LOGIN":
                    username = msg_obj.get("name", "NoName")
                    self.clients[client_socket]["name"] = username
                    print(f" {addr} đăng nhập với tên: {username}")
                    
                    # Phản hồi chào mừng riêng cho client này
                    response = {"type": "INFO", "message": f"Xin chào {username}!"}
                    client_socket.send(json.dumps(response).encode('utf-8'))

                elif msg_type == "ANSWER":
                    # [TODO] Sau này sẽ gọi hàm từ module game_logic.py của bạn TV2 tại đây
                    print(f" {self.clients[client_socket]['name']} trả lời: {msg_obj.get('choice')}")
                    # Code xử lý đáp án sẽ nằm ở đây...

                else:
                    print(f" Unknown message type: {msg_type}")

        except ConnectionResetError:
            # Lỗi này xảy ra khi Client tắt app đột ngột
            pass
        except Exception as e:
            print(f" Lỗi xử lý client {addr}: {e}")
        finally:
            # Luôn đảm bảo dọn dẹp kết nối khi vòng lặp kết thúc
            self.remove_client(client_socket)

    def start(self):
        """Vòng lặp chính chấp nhận kết nối"""
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                
                # Tạo một Thread mới cho client vừa kết nối
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.daemon = True # Thread sẽ tự tắt khi Server chính tắt
                thread.start()
                
                print(f"Active connections: {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("\n Server is shutting down...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    quiz_server = QuizServer()
    quiz_server.start()