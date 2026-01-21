import threading
import time

class GameLogic:
    def __init__(self, data_manager=None):
        """
        Khởi tạo logic game.
        :param data_manager: Đối tượng DataManager (do thành viên khác code) để lấy câu hỏi.
        """
        self.data_manager = data_manager
        self.players = {}       # Lưu: {player_id: {"name": "ABC", "score": 0}}
        self.state = "WAITING"  # Các trạng thái: WAITING, PLAYING, END
        self.current_q_index = 0
        self.time_left = 0
        self.timer_thread = None

    def add_player(self, player_id, name):
        """Thêm người chơi vào phòng chờ"""
        self.players[player_id] = {"name": name, "score": 0}
        print(f"[GAME] Player {name} (ID: {player_id}) đã tham gia.")

    def remove_player(self, player_id):
        """Xóa người chơi khi ngắt kết nối"""
        if player_id in self.players:
            print(f"[GAME] Player {self.players[player_id]['name']} đã thoát.")
            del self.players[player_id]

    def start_game(self):
        """Bắt đầu trò chơi"""
        if len(self.players) < 1:
            return False, "Cần ít nhất 1 người chơi để bắt đầu!"
        
        self.state = "PLAYING"
        self.current_q_index = 0
        # Reset điểm số
        for pid in self.players:
            self.players[pid]["score"] = 0
            
        print("[GAME] Trò chơi bắt đầu!")
        return True, "Game Start"

    def get_current_question(self):
        """Lấy câu hỏi hiện tại từ DataManager"""
        # Lưu ý: Phần này sẽ gọi data_manager của bạn Bình.
        # Tạm thời mình giả lập return câu hỏi để test logic nhé.
        if self.data_manager:
            return self.data_manager.get_question(self.current_q_index)
        else:
            # Dữ liệu giả (Mock data) để test khi chưa có DataManager
            return {
                "id": self.current_q_index,
                "text": "1 + 1 bằng mấy?",
                "options": ["1", "2", "3", "4"],
                "answer": "B"
            }

    def check_answer(self, player_id, answer_chosen, correct_answer):
        """
        Kiểm tra đáp án và cộng điểm.
        Quy tắc: Đúng +10 điểm, Sai +0.
        """
        if self.state != "PLAYING":
            return False

        if answer_chosen == correct_answer:
            self.players[player_id]["score"] += 10
            print(f"[SCORE] {self.players[player_id]['name']} +10 điểm.")
            return True
        return False

    def next_question(self):
        """Chuyển sang câu hỏi tiếp theo"""
        self.current_q_index += 1
        # Kiểm tra xem còn câu hỏi không (Logic này sẽ hoàn thiện khi nối với DataManager)
        print(f"[GAME] Chuyển sang câu hỏi số {self.current_q_index}")

    def get_leaderboard(self):
        """Trả về bảng xếp hạng sắp xếp theo điểm giảm dần"""
        # Sắp xếp dictionary players theo score
        sorted_players = sorted(
            self.players.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        return sorted_players

# --- Phần Test chạy thử (Chỉ chạy khi bạn run file này trực tiếp) ---
if __name__ == "__main__":
    game = GameLogic()
    
    # 1. Test thêm người chơi
    game.add_player("ID_01", "Dat_Tran")
    game.add_player("ID_02", "Minh_Hien")
    
    # 2. Test bắt đầu game
    game.start_game()
    
    # 3. Test trả lời (Giả sử đáp án đúng là "B")
    game.check_answer("ID_01", "B", "B") # Đạt trả lời đúng
    game.check_answer("ID_02", "A", "B") # Hiền trả lời sai
    
    # 4. In bảng xếp hạng
    print("Bảng xếp hạng:", game.get_leaderboard())