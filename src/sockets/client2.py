import socket, json, time, csv, os, statistics

class LamportClock:
    def __init__(self):
        self.clock = 0
    def tick(self):
        self.clock += 1
        return self.clock
    def update(self, received_ts):
        self.clock = max(self.clock, received_ts) + 1
        return self.clock

def send_message(host, port, sender, message, clock):
    ts = clock.tick()
    payload = json.dumps({"sender": sender, "timestamp": ts, "message": message})
    t0 = time.perf_counter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(payload.encode())
        data = s.recv(4096)
    t1 = time.perf_counter()
    resp = json.loads(data.decode())
    ts_final = clock.update(resp.get("timestamp", ts))
    return (t1 - t0) * 1000, ts_final, resp

def run_experiment(host="127.0.0.1", port=5000, sender="node1"):
    clock = LamportClock()
    exchanges = []
    latencies = []

    os.makedirs("data", exist_ok=True)

    # 20 intercambios con registro JSON
    print(f"\n--- 20 intercambios Lamport ({sender}) ---")
    for i in range(20):
        lat, ts, resp = send_message(host, port, sender, f"intercambio-{i+1}", clock)
        entry = {
            "intercambio": i + 1,
            "sender": sender,
            "timestamp_envio": ts - 1,
            "timestamp_servidor": resp.get("timestamp"),
            "timestamp_final": ts,
            "latency_ms": round(lat, 4)
        }
        exchanges.append(entry)
        print(f"  [{i+1:02d}] LT_envio={entry['timestamp_envio']} | LT_servidor={entry['timestamp_servidor']} | LT_final={ts}")

    with open(f"data/exchanges_{sender}.json", "w") as f:
        json.dump(exchanges, f, indent=2)
    print(f"  JSON guardado en data/exchanges_{sender}.json")

    # 5 envios de calentamiento
    for i in range(5):
        send_message(host, port, sender, f"warmup-{i}", clock)

    # 100 envios para medir latencia
    print(f"\n--- 100 envios latencia ({sender}) ---")
    for i in range(100):
        lat, ts, _ = send_message(host, port, sender, f"msg-{i}", clock)
        latencies.append({"iteration": i+1, "latency_ms": round(lat, 4), "lamport_ts": ts})
        print(f"  [{i+1:03d}] LT={ts:4d} | {lat:.3f} ms")

    with open("data/latency_sockets.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["iteration", "latency_ms", "lamport_ts"])
        writer.writeheader()
        writer.writerows(latencies)

    lats = [r["latency_ms"] for r in latencies]
    print(f"\n--- Resumen TCP ({sender}) ---")
    print(f"  Media:   {statistics.mean(lats):.3f} ms")
    print(f"  Mediana: {statistics.median(lats):.3f} ms")
    print(f"  Std Dev: {statistics.stdev(lats):.3f} ms")
    print(f"  CSV guardado en: data/latency_sockets.csv")

if __name__ == "__main__":
    run_experiment(port=5001, sender="node2")