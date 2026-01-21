import threading
import time

class GameLogic:
    def __init__(self, data_manager=None):
        """
        Khởi tạo logic game.
        :param data_manager: Object DataManager (từ module của Bình).
        """
        self.data_manager = data_manager
        
        # Quản lý người chơi
        self.players = {}  # {player_id: {"name": "ABC", "score": 0}}
        
        # Quản lý trạng thái game
        self.state = "WAITING"  # WAITING, PLAYING, END
        self.current_q_index = 0
        self.total_questions = 0 
        
        # Quản lý câu hỏi hiện tại
        self.current_question_data = None
        self.answered_players = set() # Set lưu ID những người đã trả lời câu hiện tại (chống spam)
        
        # Timer
        self.time_left = 0
        self.timer_active = False
        self.timer_thread = None

    # --- 1. PLAYER MANAGEMENT ---
    def add_player(self, player_id, name):
        self.players[player_id] = {"name": name, "score": 0}
        print(f"[LOGIC] Player connected: {name} ({player_id})")

    def remove_player(self, player_id):
        if player_id in self.players:
            print(f"[LOGIC] Player disconnected: {self.players[player_id]['name']}")
            del self.players[player_id]

    # --- 2. GAME FLOW CONTROL ---
    def start_game(self):
        """Thiết lập trạng thái để bắt đầu game"""
        if len(self.players) < 1:
            return False, "Cần ít nhất 1 người chơi!"
        
        # Load câu hỏi từ DataManager (nếu có)
        if self.data_manager:
            self.total_questions = self.data_manager.get_total_questions()
        else:
            self.total_questions = 5 # Mock data
            
        self.state = "PLAYING"
        self.current_q_index = 0
        
        # Reset điểm
        for pid in self.players:
            self.players[pid]["score"] = 0
            
        print("[LOGIC] Game Start! Total Questions:", self.total_questions)
        return True, "Bắt đầu game!"

    def next_question(self):
        """
        Chuẩn bị dữ liệu cho câu hỏi tiếp theo.
        Return: (is_game_over, question_payload)
        """
        if self.current_q_index >= self.total_questions:
            self.state = "END"
            return True, None # Game Over

        # Reset danh sách người đã trả lời cho câu mới
        self.answered_players.clear()
        
        # Lấy câu hỏi từ DataManager
        if self.data_manager:
            q_data = self.data_manager.get_question(self.current_q_index)
        else:
            # Mock Data cho việc test
            q_data = {
                "id": self.current_q_index,
                "text": f"Câu hỏi số {self.current_q_index + 1}: 1 + 1 = ?",
                "options": ["1", "2", "3", "4"],
                "answer": "B",
                "time": 15 # Thời gian cho câu hỏi (giây)
            }
        
        self.current_question_data = q_data
        self.current_q_index += 1
        
        # Payload gửi cho Client (Không gửi đáp án đúng!)
        payload = {
            "id": q_data["id"],
            "text": q_data["text"],
            "options": q_data["options"],
            "time_limit": q_data.get("time", 15)
        }
        
        print(f"[LOGIC] Loaded Question {self.current_q_index}")
        return False, payload

    # --- 3. TIMER SYSTEM (NEW) ---
    def start_timer(self, duration, timeout_callback):
        """
        Bắt đầu đếm ngược trong 1 thread riêng.
        :param duration: Số giây đếm ngược.
        :param timeout_callback: Hàm sẽ được gọi khi hết giờ (thường là Server gửi thông báo hết giờ).
        """
        self.time_left = duration
        self.timer_active = True
        
        # Hủy thread cũ nếu còn chạy
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_active = False
            self.timer_thread.join()

        self.timer_active = True
        self.timer_thread = threading.Thread(target=self._timer_run, args=(timeout_callback,))
        self.timer_thread.daemon = True # Thread sẽ tắt khi chương trình chính tắt
        self.timer_thread.start()

    def _timer_run(self, callback):
        """Hàm chạy ngầm của Timer"""
        print(f"[TIMER] Started countdown: {self.time_left}s")
        while self.time_left > 0 and self.timer_active:
            time.sleep(1)
            self.time_left -= 1
        
        if self.timer_active: # Nếu hết giờ mà chưa bị cancel
            print("[TIMER] Time's up!")
            self.timer_active = False
            if callback:
                callback() # Gọi hàm xử lý hết giờ bên Server

    def stop_timer(self):
        """Dừng timer (dùng khi tất cả đã trả lời xong trước giờ)"""
        self.timer_active = False

    # --- 4. ANSWER CHECKING ---
    def check_answer(self, player_id, choice):
        """
        Xử lý khi người chơi gửi đáp án.
        Return: (score_added, is_correct, correct_answer_text)
        """
        if self.state != "PLAYING" or not self.current_question_data:
            return 0, False, ""
            
        # Kiểm tra xem người này đã trả lời câu này chưa
        if player_id in self.answered_players:
            return 0, False, "ALREADY_ANSWERED"

        self.answered_players.add(player_id)
        
        correct_ans = self.current_question_data["answer"]
        is_correct = (choice == correct_ans)
        score = 0

        if is_correct:
            # Tính điểm: Có thể cộng thêm điểm dựa trên thời gian trả lời nhanh (Optional)
            score = 10 
            self.players[player_id]["score"] += score
            print(f"[SCORE] {self.players[player_id]['name']} Correct! (+{score})")
        else:
            print(f"[SCORE] {self.players[player_id]['name']} Wrong!")

        return score, is_correct, correct_ans

    def check_all_answered(self):
        """Kiểm tra xem tất cả người chơi trong phòng đã trả lời chưa"""
        return len(self.answered_players) >= len(self.players)

    def get_leaderboard(self):
        return sorted(self.players.items(), key=lambda x: x[1]['score'], reverse=True)

# --- TEST ---
if __name__ == "__main__":
    # Test Timer
    def on_timeout():
        print(">>> MAIN: Hết giờ rồi! Chuyển câu hỏi thôi.")

    game = GameLogic()
    game.add_player("P1", "Dat")
    game.start_game()
    
    # Giả lập vòng chơi
    is_over, question = game.next_question()
    print("Câu hỏi:", question)
    
    # Bắt đầu đếm ngược 5s
    game.start_timer(5, on_timeout)
    
    # Giả lập trả lời
    time.sleep(2)
    game.check_answer("P1", "B")
    
    # Chờ xem timeout có chạy không
    time.sleep(4)