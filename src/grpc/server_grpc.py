import threading
import grpc
from concurrent import futures
import messaging_pb2
import messaging_pb2_grpc

lamport_clock = 0
clock_lock = threading.Lock()

def update_clock(received_ts=0):
    global lamport_clock
    with clock_lock:
        lamport_clock = max(lamport_clock, received_ts) + 1
        return lamport_clock

class MessagingServiceServicer(messaging_pb2_grpc.MessagingServiceServicer):
    def SendMessage(self, request, context):
        ts = update_clock(request.timestamp)
        print(f"[gRPC SERVER] sender={request.sender} | LT={ts} | msg='{request.message}'")
        return messaging_pb2.MessageResponse(
            sender="server",
            timestamp=ts,
            status="OK"
        )

def serve(host="127.0.0.1", port=5002):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messaging_pb2_grpc.add_MessagingServiceServicer_to_server(
        MessagingServiceServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    print(f"[gRPC SERVER] Escuchando en {host}:{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()