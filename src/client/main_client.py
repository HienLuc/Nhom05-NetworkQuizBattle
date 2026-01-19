from network import NetworkClient

def handle_server_message(msg):
    """Hàm này sẽ được gọi mỗi khi Server gửi cái gì đó về"""
    msg_type = msg.get("type")
    
    if msg_type == "QUESTION":
        print(f"\nCâu hỏi mới: {msg['payload']['text']}")
        print(f"Lựa chọn: {msg['payload']['options']}")
    elif msg_type == "RESULT":
        print(f"\nKết quả: {msg['payload']['message']}")

# Chạy thử
client = NetworkClient()
if client.connect(callback=handle_server_message):
    # Gửi thử lệnh Login
    client.send({"type": "LOGIN", "name": "Minh Hieu"})