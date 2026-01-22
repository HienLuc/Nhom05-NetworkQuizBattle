import threading
import time

class GameLogic:
    def __init__(self, data_manager=None):
        """
        Khởi tạo logic game.
        :param data_manager: Object DataManager.
        """
        self.data_manager = data_manager
        
        # Quản lý người chơi
        self.players = {}  # {player_id: {"name": "ABC", "score": 0}}
        
        # Quản lý câu hỏi
        self.questions = [] 
        if self.data_manager:
            # Tải toàn bộ câu hỏi vào RAM ngay khi khởi động
            self.questions = self.data_manager.load_questions()
            
        self.total_questions = len(self.questions)
        self.current_q_index = 0
        
        # Quản lý trạng thái game
        self.state = "WAITING"
        self.current_question_data = None
        self.answered_players = set()
        
        # Timer
        self.time_left = 0
        self.timer_active = False
        self.timer_thread = None

    # --- 1. PLAYER MANAGEMENT ---
    def add_player(self, player_id, name):
        self.players[player_id] = {"name": name, "score": 0}
        print(f"[LOGIC] Player connected: {name}")

    def remove_player(self, player_id):
        if player_id in self.players:
            print(f"[LOGIC] Player disconnected: {self.players[player_id]['name']}")
            del self.players[player_id]

    # --- 2. GAME FLOW CONTROL ---
    def start_game(self):
        if len(self.players) < 1:
            print("⚠️ Cần ít nhất 1 người chơi để bắt đầu!")
            # return False, "Cần ít nhất 1 người chơi!" # Bỏ comment nếu muốn chặn
        
        if self.total_questions == 0:
            return False, "Chưa có dữ liệu câu hỏi!"

        self.state = "PLAYING"
        self.current_q_index = 0
        
        # Reset điểm
        for pid in self.players:
            self.players[pid]["score"] = 0
            
        return True, "Bắt đầu game!"

    def next_question(self):
        """Lấy câu hỏi tiếp theo và format dữ liệu cho Client"""
        if self.current_q_index >= self.total_questions:
            self.state = "END"
            return True, None # Game Over

        self.answered_players.clear()
        
        # Lấy câu hỏi từ danh sách
        q_data = self.questions[self.current_q_index]
        self.current_question_data = q_data
        self.current_q_index += 1
        
        # XỬ LÝ OPTIONS: Chuyển từ Dict {"A": "Đồng",...} sang List ["Đồng",...]
        # Để Client hiển thị đúng nội dung
        raw_options = q_data["options"]
        formatted_options = []
        
        if isinstance(raw_options, dict):
            # Sắp xếp theo key A, B, C, D để thứ tự không bị đảo lộn
            for key in sorted(raw_options.keys()):
                formatted_options.append(raw_options[key])
        elif isinstance(raw_options, list):
            formatted_options = raw_options

        payload = {
            "id": q_data["id"],
            "text": q_data["question"], # Key trong JSON là "question"
            "options": formatted_options,
            "time_limit": 15
        }
        
        print(f"[LOGIC] Preparing Question {self.current_q_index}: {q_data['question']}")
        return False, payload

    # --- 3. TIMER SYSTEM ---
    def start_timer(self, duration, timeout_callback):
        self.time_left = duration
        self.timer_active = True
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_active = False
            self.timer_thread.join()

        self.timer_active = True
        self.timer_thread = threading.Thread(target=self._timer_run, args=(timeout_callback,))
        self.timer_thread.daemon = True 
        self.timer_thread.start()

    def _timer_run(self, callback):
        while self.time_left > 0 and self.timer_active:
            time.sleep(1)
            self.time_left -= 1
        
        if self.timer_active: 
            self.timer_active = False
            if callback:
                callback()

    def stop_timer(self):
        self.timer_active = False

    # --- 4. ANSWER CHECKING (QUAN TRỌNG: FIX LỖI SO SÁNH) ---
    # [LOGIC ĐƠN GIẢN HÓA] Chỉ so sánh Key A, B, C, D
    def check_answer(self, player_id, choice):
        if self.state != "PLAYING" or not self.current_question_data:
            return 0, False, ""
            
        if player_id in self.answered_players:
            return 0, False, "ALREADY_ANSWERED"

        self.answered_players.add(player_id)
        
        # Lấy Key đáp án đúng (Ví dụ: "C")
        correct_key = self.current_question_data["answer"] 
        
        # Lấy Key người chơi gửi lên (Ví dụ: "C")
        player_choice = str(choice).strip().upper()
        
        print(f"[CHECK] User: '{player_choice}' vs Correct: '{correct_key}'")
        
        # SO SÁNH TRỰC TIẾP
        is_correct = (player_choice == correct_key)

        score = 0
        if is_correct:
            score = 10 
            self.players[player_id]["score"] += score
            print(f"[SCORE] {self.players[player_id]['name']} (+10 điểm)")
        else:
            print(f"[SCORE] {self.players[player_id]['name']} Sai!")

        return score, is_correct, correct_key

    def check_all_answered(self):
        return len(self.answered_players) >= len(self.players)

    def get_leaderboard(self):
        return sorted(self.players.items(), key=lambda x: x[1]['score'], reverse=True)