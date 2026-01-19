import json
import os

class DataManager:
    def __init__(self):
        # Thiết lập đường dẫn đến thư mục chứa dữ liệu
        self.data_dir = "data"
        self.q_file = os.path.join(self.data_dir, "questions.json")
        self.h_file = os.path.join(self.data_dir, "highscore.json")

    def load_questions(self):
        """Hàm đọc câu hỏi từ file JSON"""
        try:
            if os.path.exists(self.q_file):
                with open(self.q_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return [] # Trả về danh sách rỗng nếu chưa có file
        except Exception:
            return []

    def save_score(self, name, score):
        """Hàm lưu điểm của người chơi vào file JSON"""
        try:
            # Đọc dữ liệu cũ lên trước
            results = []
            if os.path.exists(self.h_file):
                with open(self.h_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            
            # Thêm kết quả mới vào danh sách
            results.append({"name": name, "score": score})
            
            # Ghi toàn bộ danh sách mới vào file
            with open(self.h_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

if __name__ == "__main__":
    # Test nhanh logic
    db = DataManager()
    print("Class DataManager đã sẵn sàng hoạt động!")
