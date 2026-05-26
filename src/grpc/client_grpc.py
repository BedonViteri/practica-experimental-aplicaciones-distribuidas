# Librerías necesarias para tiempo y JSON
import time
import json

# Librería principal de gRPC
import grpc

# Archivos generados automáticamente por protobuf
import messaging_pb2
import messaging_pb2_grpc


# Clase que implementa el reloj lógico de Lamport
class LamportClock:

    def __init__(self):
        self.clock = 0

    # Incrementa el reloj local
    def tick(self):
        self.clock += 1
        return self.clock

    # Actualiza el reloj con timestamp recibido
    def update(self, received_ts):
        self.clock = max(self.clock, received_ts) + 1
        return self.clock


# Función principal del experimento gRPC
def run_experiment(
    host="127.0.0.1",
    port=5002,
    sender="node1",
    n_measure=20,
    output_json="data/latency_grpc.json"
):

    # Inicialización del reloj lógico
    clock = LamportClock()

    # Lista para almacenar resultados
    latencies = []

    try:

        # Conexión al servidor gRPC
        with grpc.insecure_channel(f"{host}:{port}") as channel:

            # Creación del stub cliente
            stub = messaging_pb2_grpc.MessagingServiceStub(channel)

            print("\n--- Inicio de intercambio de mensajes gRPC ---\n")

            # Realiza 20 intercambios de mensajes
            for i in range(n_measure):

                # Incrementa reloj lógico
                ts_send = clock.tick()

                # Tiempo inicial
                t0 = time.perf_counter()

                # Envía mensaje al servidor
                response = stub.SendMessage(
                    messaging_pb2.MessageRequest(
                        sender=sender,
                        timestamp=ts_send,
                        message=f"msg-{i+1}"
                    )
                )

                # Tiempo final
                t1 = time.perf_counter()

                # Actualiza reloj lógico con respuesta
                ts_final = clock.update(response.timestamp)

                # Calcula latencia en milisegundos
                lat = (t1 - t0) * 1000

                # Guarda información del intercambio
                latencies.append({
                    "iteration": i + 1,
                    "message": f"msg-{i+1}",
                    "latency_ms": round(lat, 4),
                    "lamport_ts": ts_final,
                    "status": response.status
                })

                # Muestra resultado en consola
                print(
                    f"[{i+1:02d}] "
                    f"LT={ts_final:4d} | "
                    f"{lat:.3f} ms | "
                    f"status={response.status}"
                )

        # Guarda resultados en archivo JSON
        with open(output_json, "w", encoding="utf-8") as f:

            json.dump(latencies, f, indent=4)

        print(f"\nJSON guardado en: {output_json}")

    except Exception as e:

        # Captura errores generales del cliente
        print(f"\n[ERROR CLIENTE gRPC] {e}")


# Punto de entrada principal
if __name__ == "__main__":
    run_experiment()