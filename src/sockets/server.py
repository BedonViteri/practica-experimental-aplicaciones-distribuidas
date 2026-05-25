import socket, json, threading

lamport_clock = 0
clock_lock = threading.Lock()

def update_clock(received_ts=0):
    global lamport_clock
    with clock_lock:
        lamport_clock = max(lamport_clock, received_ts) + 1
        return lamport_clock

def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096)
        if data:
            msg = json.loads(data.decode())
            ts = update_clock(msg.get("timestamp", 0))
            print(f"[SERVER] De {msg['sender']} | LT={ts} | msg='{msg['message']}'")
            response = json.dumps({"sender": "server", "timestamp": ts, "message": "ACK"})
            conn.sendall(response.encode())

def start_server(host="127.0.0.1", port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(200)
        print(f"[SERVER] Escuchando en {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()