import sys
import os

# Thêm đường dẫn để tìm thấy module 'ui' và 'network' trong cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui import QuizUI

if __name__ == "__main__":
    # demo_mode=False: Chạy Client kết nối với Server thật
    # demo_mode=True: Chạy thử giao diện một mình (Mock data)
    try:
        # Bật giao diện lên -> Chương trình sẽ chạy mãi cho đến khi tắt cửa sổ
        app = QuizUI(demo_mode=False)
        app.run()
    except Exception as e:
        print(f"Lỗi khởi chạy Client: {e}")
        input("Nhấn Enter để thoát...")