import time, csv, grpc
import messaging_pb2
import messaging_pb2_grpc

class LamportClock:
    def __init__(self):
        self.clock = 0
    def tick(self):
        self.clock += 1
        return self.clock
    def update(self, received_ts):
        self.clock = max(self.clock, received_ts) + 1
        return self.clock

def run_experiment(host="127.0.0.1", port=5002, sender="node1",
                   n_warmup=5, n_measure=100, output_csv="data/latency_grpc.csv"):
    clock = LamportClock()
    latencies = []

    with grpc.insecure_channel(f"{host}:{port}") as channel:
        stub = messaging_pb2_grpc.MessagingServiceStub(channel)

        for i in range(n_warmup):
            ts = clock.tick()
            stub.SendMessage(messaging_pb2.MessageRequest(
                sender=sender, timestamp=ts, message=f"warmup-{i}"))

        for i in range(n_measure):
            ts_send = clock.tick()
            t0 = time.perf_counter()
            response = stub.SendMessage(messaging_pb2.MessageRequest(
                sender=sender, timestamp=ts_send, message=f"msg-{i}"))
            t1 = time.perf_counter()
            ts_final = clock.update(response.timestamp)
            lat = (t1 - t0) * 1000
            latencies.append({"iteration": i+1, "latency_ms": round(lat, 4), "lamport_ts": ts_final})
            print(f"  [{i+1:03d}] LT={ts_final:4d} | {lat:.3f} ms")

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["iteration", "latency_ms", "lamport_ts"])
        writer.writeheader()
        writer.writerows(latencies)

    lats = [r["latency_ms"] for r in latencies]
    import statistics
    print(f"\n--- Resumen gRPC ({sender}) ---")
    print(f"  Media:   {statistics.mean(lats):.3f} ms")
    print(f"  Mediana: {statistics.median(lats):.3f} ms")
    print(f"  Std Dev: {statistics.stdev(lats):.3f} ms")
    print(f"  CSV guardado en: {output_csv}")

if __name__ == "__main__":
    run_experiment()