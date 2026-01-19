import tkinter as tk
from tkinter import messagebox, ttk
import random


# ===================== MOCK NETWORK CLIENT =====================
class MockNetworkClient:
    """Mock client để demo UI không cần server thật"""
    def __init__(self, callback):
        self.callback = callback
        self.connected = False
        
    def connect(self):
        self.connected = True
        
    def send(self, message):
        # Giả lập phản hồi từ server
        if message["type"] == "LOGIN":
            # Sau 1s chuyển sang câu hỏi đầu tiên
            self.simulate_question(1)
            
        elif message["type"] == "ANSWER":
            # Giả lập kết quả đúng/sai ngẫu nhiên
            is_correct = random.choice([True, True, False])  # 66% đúng
            self.simulate_result(is_correct)
            
    def simulate_question(self, question_num):
        """Giả lập server gửi câu hỏi"""
        questions = [
            {
                "question": "Python là ngôn ngữ lập trình gì?",
                "options": ["Biên dịch", "Thông dịch", "Máy", "Lắp ráp"],
                "correct": "Thông dịch"
            },
            {
                "question": "Framework nào được dùng để tạo giao diện đồ họa trong Python?",
                "options": ["Django", "Flask", "Tkinter", "FastAPI"],
                "correct": "Tkinter"
            },
            {
                "question": "TCP/IP thuộc lớp nào trong mô hình OSI?",
                "options": ["Application", "Transport", "Network", "Physical"],
                "correct": "Transport"
            },
            {
                "question": "Port mặc định của HTTP là gì?",
                "options": ["80", "443", "8080", "3000"],
                "correct": "80"
            },
            {
                "question": "Socket là gì?",
                "options": ["Một cổng giao tiếp", "Một giao thức", "Một thuật toán", "Một database"],
                "correct": "Một cổng giao tiếp"
            }
        ]
        
        if question_num > len(questions):
            # Hết câu hỏi -> Game Over
            self.simulate_game_over()
            return
            
        q = questions[question_num - 1]
        self.callback({
            "type": "QUESTION",
            "question": q["question"],
            "options": q["options"],
            "question_number": question_num,
            "total_questions": len(questions),
            "_correct_answer": q["correct"]  # Dùng internal
        })
        
    def simulate_result(self, is_correct):
        """Giả lập server gửi kết quả"""
        import time
        time.sleep(0.5)  # Delay nhẹ cho realistic
        
        result = {
            "type": "RESULT",
            "correct": is_correct,
            "score": random.randint(0, 100),
        }
        
        if not is_correct:
            result["correct_answer"] = "Đáp án mẫu"
            
        self.callback(result)
        
        # Sau 2s gửi câu hỏi tiếp
        import threading
        def next_question():
            time.sleep(2)
            q_num = random.randint(2, 5)
            self.simulate_question(q_num)
        threading.Thread(target=next_question, daemon=True).start()
        
    def simulate_game_over(self):
        """Giả lập server gửi game over"""
        self.callback({
            "type": "GAME_OVER",
            "score": random.randint(60, 100),
            "leaderboard": [
                {"name": "Player1", "score": 95},
                {"name": "You", "score": random.randint(60, 90)},
                {"name": "Player3", "score": 75},
            ]
        })
        
    def close(self):
        self.connected = False


# ===================== QUIZ UI =====================
class QuizUI:
    def __init__(self, demo_mode=True):
        self.root = tk.Tk()
        self.root.title("Network Quiz Battle")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Xử lý đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Dùng Mock hoặc Real client
        if demo_mode:
            self.client = MockNetworkClient(self.handle_server_message)
        else:
            from network import NetworkClient
            self.client = NetworkClient(self.handle_server_message)

        self.username = ""
        self.current_question = None
        self.selected_answer = tk.StringVar()
        self.score = 0
        self.total_questions = 0
        self.answered = False  # Tránh spam answer

        self.build_login_screen()
 
    # ===================== LOGIN SCREEN =====================
    def build_login_screen(self):
        self.clear_screen()

        # Header
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🎮 NETWORK QUIZ BATTLE",
                 font=("Arial", 20, "bold"),
                 bg="#4A90E2", fg="white").pack(expand=True)

        # Form frame
        form_frame = tk.Frame(self.root)
        form_frame.pack(expand=True)

        tk.Label(form_frame, text="Nhập tên người chơi:",
                 font=("Arial", 14)).pack(pady=20)

        self.name_entry = tk.Entry(form_frame, font=("Arial", 14), width=20)
        self.name_entry.pack(pady=10)
        self.name_entry.focus()
        
        # Bind Enter key
        self.name_entry.bind('<Return>', lambda e: self.login())

        tk.Button(form_frame, text="🚀 Bắt đầu",
                  font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white",
                  padx=30, pady=10,
                  command=self.login).pack(pady=30)

    def login(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("⚠️ Lỗi", "Vui lòng nhập tên!")
            self.name_entry.focus()
            return

        if len(name) > 20:
            messagebox.showwarning("⚠️ Lỗi", "Tên không được quá 20 ký tự!")
            return

        self.username = name
        
        # Kết nối với xử lý lỗi
        try:
            self.client.connect()
            self.client.send({
                "type": "LOGIN",
                "username": self.username
            })
            self.build_waiting_screen()
        except Exception as e:
            messagebox.showerror("❌ Lỗi kết nối", 
                               f"Không thể kết nối đến server:\n{str(e)}")
            return

    # ===================== WAITING SCREEN =====================
    def build_waiting_screen(self):
        self.clear_screen()

        # Header
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"👋 Xin chào, {self.username}!",
                 font=("Arial", 16, "bold"),
                 bg="#4A90E2", fg="white").pack(expand=True)

        # Waiting content
        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        tk.Label(content_frame, text="⏳ Đang chờ người chơi khác...",
                 font=("Arial", 14)).pack(pady=30)
        
        # Progress bar animation
        progress = ttk.Progressbar(content_frame, mode='indeterminate', length=300)
        progress.pack(pady=20)
        progress.start(10)

    # ===================== QUIZ SCREEN =====================
    def build_quiz_screen(self, question_data):
        self.clear_screen()

        self.current_question = question_data
        self.selected_answer.set("")
        self.answered = False

        # Header với progress
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        info_frame = tk.Frame(header_frame, bg="#4A90E2")
        info_frame.pack(expand=True, fill="both", padx=20)
        
        tk.Label(info_frame, 
                text=f"Câu {question_data.get('question_number', '?')}/{question_data.get('total_questions', '?')}",
                font=("Arial", 12, "bold"),
                bg="#4A90E2", fg="white").pack(side="left")
        
        tk.Label(info_frame, 
                text=f"Điểm: {self.score}",
                font=("Arial", 12, "bold"),
                bg="#4A90E2", fg="white").pack(side="right")

        # Question frame
        question_frame = tk.Frame(self.root, bg="#f0f0f0")
        question_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(question_frame, text="❓ Câu hỏi:",
                 font=("Arial", 12, "bold"),
                 bg="#f0f0f0").pack(anchor="w", pady=(10, 5))

        tk.Label(question_frame, text=question_data["question"],
                 wraplength=500,
                 font=("Arial", 13),
                 bg="#f0f0f0",
                 justify="left").pack(anchor="w", pady=10, padx=10)

        # Options
        options_frame = tk.Frame(question_frame, bg="#f0f0f0")
        options_frame.pack(fill="both", expand=True, pady=10)

        for i, option in enumerate(question_data["options"]):
            rb = tk.Radiobutton(
                options_frame,
                text=f"{chr(65+i)}. {option}",  # A. B. C. D.
                variable=self.selected_answer,
                value=option,
                font=("Arial", 12),
                bg="#f0f0f0",
                activebackground="#e0e0e0",
                selectcolor="#4CAF50"
            )
            rb.pack(anchor="w", padx=30, pady=5)

        # Submit button
        self.submit_btn = tk.Button(self.root, text="✓ Gửi đáp án",
                  font=("Arial", 13, "bold"),
                  bg="#4CAF50", fg="white",
                  padx=40, pady=12,
                  command=self.submit_answer)
        self.submit_btn.pack(pady=20)

    def submit_answer(self):
        answer = self.selected_answer.get()
        if not answer:
            messagebox.showwarning("⚠️ Lỗi", "Bạn chưa chọn đáp án!")
            return

        if self.answered:
            return  # Tránh spam

        self.answered = True
        self.submit_btn.config(state="disabled", bg="gray")

        try:
            self.client.send({
                "type": "ANSWER",
                "answer": answer
            })
        except Exception as e:
            messagebox.showerror("❌ Lỗi", f"Không thể gửi đáp án:\n{str(e)}")
            self.answered = False
            self.submit_btn.config(state="normal", bg="#4CAF50")

    # ===================== RESULT SCREEN =====================
    def show_result(self, result_data):
        self.clear_screen()

        self.score = result_data.get('score', self.score)
        is_correct = result_data.get("correct", False)
        
        # Header
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"Điểm hiện tại: {self.score}",
                 font=("Arial", 16, "bold"),
                 bg="#4A90E2", fg="white").pack(expand=True)

        # Result content
        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        if is_correct:
            result_text = "🎉 CHÍNH XÁC!"
            color = "#4CAF50"
        else:
            result_text = "❌ SAI RỒI!"
            color = "#F44336"

        tk.Label(content_frame, text=result_text,
                 font=("Arial", 28, "bold"),
                 fg=color).pack(pady=40)

        # Hiển thị đáp án đúng nếu sai
        if not is_correct and "correct_answer" in result_data:
            tk.Label(content_frame, 
                    text=f"Đáp án đúng: {result_data['correct_answer']}",
                    font=("Arial", 13),
                    fg="#666").pack(pady=10)

        tk.Label(content_frame, text="⏳ Chờ câu hỏi tiếp theo...",
                 font=("Arial", 12),
                 fg="#666").pack(pady=20)

    # ===================== GAME OVER SCREEN =====================
    def show_game_over(self, message):
        self.clear_screen()

        # Header
        header_frame = tk.Frame(self.root, bg="#F44336", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🏁 GAME OVER",
                 font=("Arial", 24, "bold"),
                 bg="#F44336", fg="white").pack(expand=True)

        # Result content
        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        tk.Label(content_frame, text=f"Điểm cuối cùng: {message.get('score', self.score)}",
                 font=("Arial", 18, "bold")).pack(pady=30)

        # Leaderboard nếu có
        if "leaderboard" in message:
            tk.Label(content_frame, text="📊 Bảng xếp hạng:",
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            for i, player in enumerate(message["leaderboard"], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                tk.Label(content_frame, 
                        text=f"{medal} {i}. {player['name']}: {player['score']} điểm",
                        font=("Arial", 12)).pack()

        # Buttons
        btn_frame = tk.Frame(content_frame)
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="🔄 Chơi lại",
                  font=("Arial", 12, "bold"),
                  bg="#4CAF50", fg="white",
                  padx=20, pady=10,
                  command=self.restart_game).pack(side="left", padx=10)

        tk.Button(btn_frame, text="🚪 Thoát",
                  font=("Arial", 12, "bold"),
                  bg="#F44336", fg="white",
                  padx=20, pady=10,
                  command=self.quit_game).pack(side="left", padx=10)

    # ===================== SERVER MESSAGE HANDLER =====================
    def handle_server_message(self, message):
        """
        Hàm này được gọi từ thread network
        -> phải đưa về main thread bằng root.after
        """
        self.root.after(0, self.process_message, message)

    def process_message(self, message):
        msg_type = message.get("type")

        if msg_type == "QUESTION":
            self.build_quiz_screen(message)

        elif msg_type == "RESULT":
            self.show_result(message)

        elif msg_type == "GAME_OVER":
            self.show_game_over(message)

        elif msg_type == "ERROR":
            messagebox.showerror("❌ Lỗi", message.get("message", "Lỗi không xác định"))

    # ===================== UTILS =====================
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def restart_game(self):
        self.score = 0
        self.total_questions = 0
        self.answered = False
        self.build_login_screen()

    def quit_game(self):
        self.on_closing()

    def on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
            try:
                self.client.close()
            except:
                pass
            self.root.destroy()

    def run(self):
        self.root.mainloop()


# ===================== MAIN =====================
if __name__ == "__main__":
    # Chạy ở chế độ demo (không cần server)
    app = QuizUI(demo_mode=True)
    app.run()