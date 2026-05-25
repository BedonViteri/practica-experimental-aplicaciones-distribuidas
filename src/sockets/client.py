import socket, json, time, csv

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
    return (t1 - t0) * 1000, ts_final

def run_experiment(host="127.0.0.1", port=5000, sender="node1",
                   n_warmup=5, n_measure=100, output_csv="data/latency_sockets.csv"):
    clock = LamportClock()
    latencies = []

    for i in range(n_warmup):
        send_message(host, port, sender, f"warmup-{i}", clock)

    for i in range(n_measure):
        lat, ts = send_message(host, port, sender, f"msg-{i}", clock)
        latencies.append({"iteration": i+1, "latency_ms": round(lat, 4), "lamport_ts": ts})
        print(f"  [{i+1:03d}] LT={ts:4d} | {lat:.3f} ms")

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["iteration", "latency_ms", "lamport_ts"])
        writer.writeheader()
        writer.writerows(latencies)

    lats = [r["latency_ms"] for r in latencies]
    import statistics
    print(f"\n--- Resumen TCP ({sender}) ---")
    print(f"  Media:   {statistics.mean(lats):.3f} ms")
    print(f"  Mediana: {statistics.median(lats):.3f} ms")
    print(f"  Std Dev: {statistics.stdev(lats):.3f} ms")
    print(f"  CSV guardado en: {output_csv}")

if __name__ == "__main__":
    run_experiment()