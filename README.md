# 🎮 Nhom[DienSoNhom]-NetworkQuizBattle

> Đồ án giữa kỳ môn Lập trình mạng | Mini Game: Đấu Trường Tri Thức (Network Quiz)

![Python](https://img.shields.io/badge/Language-Python_3.x-blue?style=flat-square)
![Tech](https://img.shields.io/badge/Tech-TCP_Socket_MultiThreading-green?style=flat-square)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange?style=flat-square)

## 📖 Giới thiệu (Overview)

Dự án xây dựng một hệ thống Game Quiz Multiplayer theo mô hình **Client-Server** sử dụng Python. 
Server đóng vai trò là Host (MC), quản lý bộ câu hỏi và tính điểm. Các Client kết nối vào phòng chờ, nhận câu hỏi cùng lúc và thi đua trả lời để giành điểm số cao nhất.

### Tính năng chính

- **Multi-Client:** Hỗ trợ nhiều người chơi kết nối đồng thời (Sử dụng Multi-threading).
- **Real-time:** Câu hỏi được đẩy từ Server xuống tất cả Client cùng lúc.
- **Scoring:** Hệ thống tính điểm tự động và cập nhật bảng xếp hạng ngay lập tức.
- **Protocol:** Giao tiếp qua TCP/IP bằng định dạng JSON.

---

## 🚀 Hướng dẫn Cài đặt & Chạy (Getting Started)

### 1. Yêu cầu hệ thống

- **Python 3.8+**
- Thư viện chuẩn (Built-in): `socket`, `threading`, `json`, `tkinter` (thường có sẵn khi cài Python, không cần pip install thêm).

### 2. Cách chạy chương trình

**Bước 1: Khởi động Server** (Chạy trên máy Host)

Mở terminal tại thư mục gốc của dự án:

```bash
python src/server.py
```

Server sẽ bắt đầu lắng nghe tại `127.0.0.1:65432`

**Bước 2: Khởi động Client** (Mở terminal mới cho mỗi người chơi)

```bash
python src/client/main_client.py
```

Giao diện đăng nhập hiện ra → Nhập tên → Bắt đầu chơi.

---

## 📅 Phân Công Thành Viên (Team Roles)

| Thành viên | Role | Nhiệm vụ chi tiết (Scope of Work) | Nhánh Git (Branch) |
|-----------|------|-----------------------------------|--------------------|
| Lục Sỹ Minh Hiền | Leader / Server Core | Code server.py: Socket bind, listen. Xử lý đa luồng (threading) cho nhiều Client. Quản lý danh sách kết nối. | `feature/server-core` |
| Trần Phát Đạt | Game Logic | Tạo file questions.json. Code Logic: Check đáp án đúng/sai, tính điểm. Xử lý trạng thái (Chờ, Đang chơi, Kết thúc). | `feature/game-logic` |
| Thành viên 3 | Client Network | Code lớp mạng phía Client (Connect, Send, Receive). Xử lý luồng nhận dữ liệu (Background Thread) để không treo UI. | `feature/client-net` |
| Sim Lưu Gia Bảo | Frontend (GUI) | Code giao diện Tkinter. Thiết kế màn hình: Login, Quiz (Câu hỏi + 4 nút), Kết quả. Hiển thị dữ liệu từ Server lên màn hình. | `feature/client-ui` |
| Thành viên 5 | Protocol & QC | Định nghĩa JSON Schema. Test kết nối giữa các máy. Merge code và viết tài liệu báo cáo. | `feature/protocol-tests` |

---

## 🛠️ Quy Trình Git (Git Workflow)

Để đảm bảo code sạch và dễ chấm điểm:

- **Main Branch:** Chỉ chứa code hoàn chỉnh, chạy ổn định.
- **Dev Branch:** Nhánh tích hợp code chung trước khi đưa vào Main.
- **Feature Branch:** Mỗi thành viên code trên nhánh riêng (như bảng trên).
- **Commit Message Rule:** `[Module] Description`. VD: `[UI] Design login screen`, `[Server] Fix thread crash`.

---

## 📂 Cấu Trúc Thư Mục (Project Structure)

```text
Nhom 5-NetworkQuizBattle/
├── data/
│   └── questions.json         # Cơ sở dữ liệu câu hỏi
├── src/
│   ├── __init__.py
│   ├── server.py              # [TV1] Code chạy Server
│   ├── game_logic.py           # [TV2] Class xử lý luật chơi
│   └── client/
│       ├── __init__.py
│       ├── main_client.py      # [TV3+4] Code chạy Client (Main)
│       ├── network.py          # [TV3] Class xử lý Socket Client
│       └── ui.py               # [TV4] Class giao diện Tkinter
├── tests/                      # [TV5] Script test nhanh kết nối
├── README.md                   # Tài liệu dự án
└── .gitignore                  # File cấu hình git ignore
```

---

## 📡 Giao Thức Giao Tiếp (JSON Protocol)

Mọi dữ liệu gửi qua Socket đều được mã hóa `utf-8` dưới dạng JSON String.

### 1. Client gửi Server (Request)

**Đăng nhập:**

```json
{
    "type": "LOGIN",
    "name": "NguyenVanA"
}
```

**Gửi câu trả lời:**

```json
{
    "type": "ANSWER",
    "question_id": 1,
    "choice": "B"
}
```

### 2. Server gửi Client (Response)

**Gửi câu hỏi:**

```json
{
    "type": "QUESTION", 
    "payload": {
        "id": 1, 
        "text": "Thủ đô của Việt Nam?", 
        "options": ["Hà Nội", "Đà Nẵng", "TP.HCM", "Cần Thơ"]
    }
}
```

**Thông báo kết quả:**

```json
{
    "type": "RESULT", 
    "payload": {
        "status": "CORRECT", 
        "score": 10,
        "message": "Chính xác! Bạn được cộng 10 điểm."
    }
}
```

---

## 📝 Ghi chú

- Mỗi thành viên tạo branch riêng theo quy ước trên.
- Commit thường xuyên với message rõ ràng.
- Trước khi merge vào `dev`, hãy test kỹ lưỡng.
- Khi hoàn thành toàn bộ dự án, merge `dev` vào `main`.

---

**Happy Coding! 🚀**
