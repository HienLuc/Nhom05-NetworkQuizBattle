import socket
import threading
import json

class NetworkClient:
    # SỬA 1: Thêm tham số callback vào hàm khởi tạo __init__
    def __init__(self, callback, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False
        self.callback = callback # Lưu hàm callback ngay từ đầu

    # SỬA 2: Hàm connect không cần nhận callback nữa
    def connect(self):
        """Kết nối tới server và bắt đầu luồng nhận dữ liệu."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            # Tạo luồng phụ để nhận tin nhắn từ Server
            receive_thread = threading.Thread(target=self._receive_loop)
            receive_thread.daemon = True # Tự tắt khi chương trình chính tắt
            receive_thread.start()
            return True
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            # Có thể ném lỗi ra ngoài để UI bắt được và hiện thông báo
            raise e

    def _receive_loop(self):
        """Luồng chạy ngầm để nhận dữ liệu JSON liên tục."""
        while self.running:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                # Parse JSON string thành Python dict
                message = json.loads(data)
                
                # Gửi dữ liệu về UI thông qua hàm callback
                if self.callback:
                    self.callback(message)
                    
            except Exception as e:
                print(f"Lỗi nhận dữ liệu: {e}")
                self.running = False
                break

    def send(self, data_dict):
        """Gửi dữ liệu từ Client lên Server (dưới dạng JSON)."""
        if self.client_socket:
            try:
                json_data = json.dumps(data_dict)
                self.client_socket.sendall(json_data.encode('utf-8'))
            except Exception as e:
                print(f"Lỗi gửi dữ liệu: {e}")

    def close(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()