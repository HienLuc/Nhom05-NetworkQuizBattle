import tkinter as tk
from tkinter import messagebox, ttk
import random

#MOCK NETWORK CLIENT
class MockNetworkClient:
    """Mock client để demo UI không cần server thật"""
    def __init__(self, callback):
        self.callback = callback
        self.connected = False
        
    def connect(self):
        self.connected = True
        
    def send(self, message):
        if message["type"] == "LOGIN":
            self.simulate_question(1)
            
        elif message["type"] == "ANSWER":
            is_correct = random.choice([True, False])
            self.simulate_result(is_correct)
            
    def simulate_question(self, question_num):
        questions = [
            {"question": "Test câu 1", "options": ["Opt A", "Opt B", "Opt C", "Opt D"], "correct": "B"}
        ]
        if question_num <= len(questions):
            q = questions[question_num - 1]
            self.callback({
                "type": "QUESTION",
                "question": q["question"],
                "options": q["options"],
                "question_number": question_num,
                "total_questions": len(questions)
            })
        else:
            self.simulate_game_over()
            
    def simulate_result(self, is_correct):
        import time
        time.sleep(0.5)
        self.callback({
            "type": "RESULT",
            "correct_answer": "B",
            "score": 10 if is_correct else 0
        })
        
    def simulate_game_over(self):
        self.callback({"type": "GAME_OVER", "score": 100, "leaderboard": []})
        
    def close(self):
        self.connected = False


#QUIZ UI
class QuizUI:
    def __init__(self, demo_mode=True):
        self.root = tk.Tk()
        self.root.title("Network Quiz Battle")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        #Căn giữa màn hình cho chuyên nghiệp
        self.center_window()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.answered = False 

        self.build_login_screen()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    #LOGIN SCREEN
    def build_login_screen(self):
        self.clear_screen()

        header_frame = tk.Frame(self.root, bg="#4A90E2", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=" NETWORK QUIZ BATTLE",
                 font=("Arial", 20, "bold"),
                 bg="#4A90E2", fg="white").pack(expand=True)

        form_frame = tk.Frame(self.root)
        form_frame.pack(expand=True)

        tk.Label(form_frame, text="Nhập tên người chơi:", font=("Arial", 14)).pack(pady=20)

        self.name_entry = tk.Entry(form_frame, font=("Arial", 14), width=20)
        self.name_entry.pack(pady=10)
        self.name_entry.focus()
        self.name_entry.bind('<Return>', lambda e: self.login())

        tk.Button(form_frame, text=" Bắt đầu",
                  font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white",
                  padx=30, pady=10,
                  command=self.login).pack(pady=30)

    def login(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(" Lỗi", "Vui lòng nhập tên!")
            return

        self.username = name
        try:
            self.client.connect()
            self.client.send({
                "type": "LOGIN",
                "name": self.username
            })
            self.build_waiting_screen()
        except Exception as e:
            messagebox.showerror(" Lỗi kết nối", f"Không thể kết nối Server:\n{e}")

    #WAITING SCREEN
    def build_waiting_screen(self):
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text=f" Xin chào, {self.username}!",
                 font=("Arial", 16, "bold"), bg="#4A90E2", fg="white").pack(expand=True, fill="both")

        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        tk.Label(content_frame, text=" Đang chờ người chơi khác...", font=("Arial", 14)).pack(pady=30)
        
        progress = ttk.Progressbar(content_frame, mode='indeterminate', length=300)
        progress.pack(pady=20)
        progress.start(10)

    #QUIZ SCREEN
    def build_quiz_screen(self, question_data):
        self.clear_screen()
        self.current_question = question_data
        self.selected_answer.set("")
        self.answered = False

        # Info Header
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        
        info_frame = tk.Frame(header_frame, bg="#4A90E2")
        info_frame.pack(expand=True, fill="both", padx=20)
        
        tk.Label(info_frame, 
                text=f"Câu {question_data.get('question_number', '?')}/{question_data.get('total_questions', '?')}",
                font=("Arial", 12, "bold"), bg="#4A90E2", fg="white").pack(side="left")
        
        tk.Label(info_frame, text=f"Điểm: {self.score}",
                font=("Arial", 12, "bold"), bg="#4A90E2", fg="white").pack(side="right")

        # Question Body
        question_frame = tk.Frame(self.root, bg="#f0f0f0")
        question_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(question_frame, text=" Câu hỏi:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))
        
        tk.Label(question_frame, text=question_data["question"],
                 wraplength=500, font=("Arial", 13), bg="#f0f0f0", justify="left").pack(anchor="w", pady=10, padx=10)

        options_frame = tk.Frame(question_frame, bg="#f0f0f0")
        options_frame.pack(fill="both", expand=True, pady=10)

        for i, option_text in enumerate(question_data["options"]):
            option_key = chr(65 + i) # 0->A, 1->B...
            
            rb = tk.Radiobutton(
                options_frame,
                text=f"{option_key}. {option_text}",
                variable=self.selected_answer,
                value=option_key,  
                font=("Arial", 12),
                bg="#f0f0f0",
                activebackground="#e0e0e0",
                selectcolor="#4CAF50"
            )
            rb.pack(anchor="w", padx=30, pady=5)

        self.submit_btn = tk.Button(self.root, text="✓ Gửi đáp án",
                  font=("Arial", 13, "bold"), bg="#4CAF50", fg="white",
                  padx=40, pady=12, command=self.submit_answer)
        self.submit_btn.pack(pady=20)

    def submit_answer(self):
        answer = self.selected_answer.get()
        if not answer:
            messagebox.showwarning(" Lỗi", "Bạn chưa chọn đáp án!")
            return

        if self.answered: return 
        self.answered = True
        self.submit_btn.config(state="disabled", bg="gray")

        try:
            self.client.send({
                "type": "ANSWER",
                "answer": answer
            })
        except Exception as e:
            messagebox.showerror(" Lỗi", str(e))
            self.answered = False

    #RESULT SCREEN
    def show_result(self, result_data):
        self.clear_screen()
        self.score = result_data.get('score', self.score)
        
        #Logic kiểm tra đúng sai tại Client để hiển thị màu
        server_correct_ans = result_data.get("correct_answer", "")
        my_ans = self.selected_answer.get()
        
        # Nếu đáp án mình chọn (my_ans) trùng với Server (correct_ans) thì là Đúng
        is_correct = (my_ans == server_correct_ans) and (my_ans != "")

        # Header
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=80)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=f"Điểm hiện tại: {self.score}",
                 font=("Arial", 16, "bold"), bg="#4A90E2", fg="white").pack(expand=True)

        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        if is_correct:
            tk.Label(content_frame, text=" CHÍNH XÁC!", font=("Arial", 28, "bold"), fg="#4CAF50").pack(pady=40)
        else:
            tk.Label(content_frame, text=" SAI RỒI!", font=("Arial", 28, "bold"), fg="#F44336").pack(pady=40)
            tk.Label(content_frame, text=f"Đáp án đúng: {server_correct_ans}", 
                    font=("Arial", 13), fg="#666").pack(pady=10)

        tk.Label(content_frame, text=" Chờ câu hỏi tiếp theo...", font=("Arial", 12), fg="#666").pack(pady=20)

    #GAME OVER
    def show_game_over(self, message):
        self.clear_screen()
        header_frame = tk.Frame(self.root, bg="#F44336", height=100)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=" GAME OVER", font=("Arial", 24, "bold"), bg="#F44336", fg="white").pack(expand=True)

        content_frame = tk.Frame(self.root)
        content_frame.pack(expand=True)

        tk.Label(content_frame, text=f"Điểm cuối cùng: {message.get('score', self.score)}",
                 font=("Arial", 18, "bold")).pack(pady=30)

        if "leaderboard" in message:
            tk.Label(content_frame, text=" Bảng xếp hạng:", font=("Arial", 14, "bold")).pack(pady=10)
            for i, player in enumerate(message["leaderboard"], 1):
                medal = "" if i==1 else "🥈" if i==2 else "🥉" if i==3 else "  "
                tk.Label(content_frame, text=f"{medal} {i}. {player['name']}: {player['score']}").pack()

        btn_frame = tk.Frame(content_frame)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="🔄 Chơi lại", font=("Arial", 12), bg="#4CAF50", fg="white", padx=20, command=self.restart_game).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🚪 Thoát", font=("Arial", 12), bg="#F44336", fg="white", padx=20, command=self.quit_game).pack(side="left", padx=10)

    #HANDLERS & UTILS
    def handle_server_message(self, message):
        self.root.after(0, self.process_message, message)

    def process_message(self, message):
        msg_type = message.get("type")
        if msg_type == "QUESTION": self.build_quiz_screen(message)
        elif msg_type == "RESULT": self.show_result(message)
        elif msg_type == "GAME_OVER": self.show_game_over(message)
        elif msg_type == "ERROR": messagebox.showerror(" Lỗi", message.get("message"))

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def restart_game(self):
        self.score = 0
        self.build_login_screen()

    def quit_game(self):
        self.on_closing()

    def on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn muốn thoát game?"):
            try: self.client.close()
            except: pass
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = QuizUI(demo_mode=True)
    app.run()