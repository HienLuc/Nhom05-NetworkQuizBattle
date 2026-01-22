import socket
import threading
import json
import time
import sys
import os

# --- IMPORT MODULES CỦA THÀNH VIÊN KHÁC ---
# Thêm đường dẫn để import được file trong cùng thư mục src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import GameLogic
from data_manager import DataManager

# Cấu hình Server
HOST = '127.0.0.1' # Hoặc '0.0.0.0' để chạy LAN
PORT = 65432

class QuizServer:
    def __init__(self):
        # 1. Khởi tạo kết nối mạng
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Tránh lỗi "Address already in use"
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        
        # 2. Quản lý Client: {client_socket: {"addr":..., "name":...}}
        self.clients = {} 
        
        # 3. Tích hợp Data & Logic (Core của Server)
        self.db = DataManager()
        self.game = GameLogic(self.db)
        
        # Biến điều khiển vòng lặp game
        self.is_game_running = False

        print(f" Server đang chạy tại {HOST}:{PORT}")
        print(f" Đã tải dữ liệu: {self.game.total_questions} câu hỏi.")
        print(" Gõ 'start' vào terminal này để bắt đầu game khi đủ người!")

    def broadcast(self, message_dict, exclude_socket=None):
        """Gửi tin nhắn JSON cho TOÀN BỘ client"""
        try:
            msg_bytes = json.dumps(message_dict).encode('utf-8')
            for client_sock in list(self.clients.keys()):
                if client_sock != exclude_socket:
                    try:
                        client_sock.sendall(msg_bytes)
                    except:
                        self.remove_client(client_sock)
        except Exception as e:
            print(f" Broadcast Error: {e}")

    def send_to_client(self, client_socket, message_dict):
        """Gửi tin nhắn cho 1 Client cụ thể"""
        try:
            msg_bytes = json.dumps(message_dict).encode('utf-8')
            client_socket.sendall(msg_bytes)
        except:
            pass

    def remove_client(self, client_socket):
        """Xử lý khi client ngắt kết nối"""
        if client_socket in self.clients:
            name = self.clients[client_socket]["name"]
            print(f" {name} đã thoát.")
            
            # Xóa khỏi Logic game và Danh sách mạng
            self.game.remove_player(client_socket) 
            del self.clients[client_socket]
            client_socket.close()
            
            # Cập nhật số lượng người chơi cho mọi người
            self.broadcast({"type": "INFO", "message": f"{name} đã rời phòng."})

    def handle_client(self, client_socket, addr):
        """Luồng xử lý riêng cho từng người chơi"""
        print(f"➕ Kết nối mới: {addr}")
        self.clients[client_socket] = {"addr": addr, "name": "Unknown"}

        try:
            while True:
                data = client_socket.recv(1024)
                if not data: break

                try:
                    msg_obj = json.loads(data.decode('utf-8'))
                    msg_type = msg_obj.get("type")

                    # --- XỬ LÝ GÓI TIN TỪ CLIENT ---
                    
                    if msg_type == "LOGIN":
                        # 1. Đăng nhập
                        username = msg_obj.get("name", "NoName")
                        self.clients[client_socket]["name"] = username
                        
                        # Thêm vào Logic Game
                        self.game.add_player(client_socket, username)
                        
                        print(f" {username} đã tham gia.")
                        self.send_to_client(client_socket, {"type": "LOGIN_OK", "message": "Chào mừng!"})
                        self.broadcast({"type": "INFO", "message": f"{username} đã vào phòng chờ."})

                    elif msg_type == "ANSWER":
                        # 2. Nhận đáp án
                        choice = msg_obj.get("answer") # Chú ý: UI gửi key là "answer"
                        # Gọi Logic để chấm điểm
                        score, is_correct, correct_ans = self.game.check_answer(client_socket, choice)
                        # (Kết quả sẽ được gửi chung sau khi hết giờ, không gửi ngay để tránh lộ)

                except json.JSONDecodeError:
                    continue
        except:
            pass
        finally:
            self.remove_client(client_socket)

    def game_loop(self):
        """VÒNG LẶP TRÒ CHƠI (GAME LOOP) - Phần quan trọng nhất"""
        print("\n GAME BẮT ĐẦU!")
        self.is_game_running = True
        
        # Gọi logic bắt đầu
        success, msg = self.game.start_game()
        if not success:
            print(f" Không thể bắt đầu: {msg}")
            self.is_game_running = False
            return

        # Vòng lặp từng câu hỏi
        while self.is_game_running:
            # 1. Lấy câu hỏi tiếp theo
            is_over, question_payload = self.game.next_question()
            
            if is_over:
                break # Hết câu hỏi -> Kết thúc
            
            # 2. Format dữ liệu cho đúng chuẩn UI Client yêu cầu
            # UI cần: type, question, options, question_number, total_questions
            client_payload = {
                "type": "QUESTION",
                "question": question_payload["text"],
                "options": question_payload["options"],
                "question_number": self.game.current_q_index,
                "total_questions": self.game.total_questions,
                "time_limit": question_payload.get("time_limit", 15)
            }
            
            # 3. Gửi câu hỏi cho tất cả
            print(f" Đang gửi câu hỏi {self.game.current_q_index}...")
            self.broadcast(client_payload)
            
            # 4. Đếm ngược (Thời gian trả lời)
            time_limit = question_payload.get("time_limit", 10)
            for i in range(time_limit, 0, -1):
                # (Optional) Có thể gửi tick thời gian nếu muốn
                time.sleep(1)
                # Kiểm tra nếu tất cả đã trả lời thì skip
                if self.game.check_all_answered():
                    print("⚡ Tất cả đã trả lời sớm!")
                    break
            
            # 5. Gửi KẾT QUẢ (Sau khi hết giờ)
            print(" Hết giờ! Đang gửi kết quả...")
            
            # Duyệt từng người để gửi kết quả riêng (Vì điểm số khác nhau)
            for player_sock in list(self.clients.keys()):
                player_info = self.game.players.get(player_sock)
                if player_info:
                    # Lấy thông tin đáp án đúng hiện tại từ Logic
                    current_q_data = self.game.current_question_data
                    correct_ans = current_q_data["answer"]
                    
                    # Logic kiểm tra xem user này đúng hay sai (để UI hiện màu đỏ/xanh)
                    # Lưu ý: Logic đã tính điểm lúc nhận ANSWER rồi, giờ chỉ cần lấy Score tổng
                    
                    # Gửi gói tin RESULT
                    # Cần xác định user này trả lời đúng hay sai ở câu vừa rồi để UI hiện
                    # Tuy nhiên, server đơn giản hóa bằng cách gửi đáp án đúng, UI tự so sánh nếu cần
                    # Hoặc tốt nhất: Server báo luôn Đúng/Sai.
                    
                    # (Ở đây ta gửi đáp án đúng và bảng điểm, UI sẽ tự hiện)
                    res_payload = {
                        "type": "RESULT",
                        "correct_answer": correct_ans, # Đáp án đúng (VD: "A")
                        "score": player_info["score"], # Tổng điểm hiện tại
                        "correct": False # UI sẽ cần logic này, nhưng tạm thời gửi chung
                    }
                    # *Nâng cao: Để biết chính xác user đó đúng hay sai, cần lưu history trong Logic
                    # Tạm thời gửi đáp án đúng về cho Client tự so sánh với lựa chọn của mình
                    
                    self.send_to_client(player_sock, res_payload)
            
            # Nghỉ 3 giây trước câu tiếp theo
            time.sleep(3)

        # --- KẾT THÚC GAME ---
        print(" Game Over!")
        leaderboard = self.game.get_leaderboard()
        
        # Format bảng xếp hạng cho Client
        # leaderboard từ logic trả về list các tuple: [(sock, info), ...]
        leaderboard_data = []
        for sock, info in leaderboard:
            leaderboard_data.append({"name": info["name"], "score": info["score"]})
            
            # Lưu điểm cao (Gọi DataManager)
            self.db.save_score(info["name"], info["score"])

        end_msg = {
            "type": "GAME_OVER",
            "message": "Trò chơi kết thúc!",
            "leaderboard": leaderboard_data
        }
        self.broadcast(end_msg)
        self.is_game_running = False

    def admin_input_loop(self):
        """Luồng lắng nghe lệnh từ Admin (Server Console)"""
        while True:
            cmd = input()
            if cmd.strip().lower() == "start":
                if not self.is_game_running:
                    # Chạy Game Loop trong luồng riêng để không chặn input
                    threading.Thread(target=self.game_loop).start()
                else:
                    print(" Game đang chạy rồi!")
            elif cmd.strip().lower() == "stop":
                self.is_game_running = False
                print(" Đang dừng game...")

    def start(self):
        # 1. Luồng Admin Input
        threading.Thread(target=self.admin_input_loop, daemon=True).start()
        
        # 2. Vòng lặp chính chấp nhận kết nối
        try:
            while True:
                client_sock, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_sock, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = QuizServer()
    server.start()