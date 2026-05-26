# Librería para manejo de hilos
import threading

# Librería principal de gRPC
import grpc

# Permite manejar múltiples conexiones concurrentes
from concurrent import futures

# Archivos generados automáticamente por protobuf
import messaging_pb2
import messaging_pb2_grpc

# Inicialización del reloj lógico de Lamport
lamport_clock = 0

# Lock para evitar problemas de concurrencia entre hilos
clock_lock = threading.Lock()


# Función para actualizar el reloj lógico de Lamport
def update_clock(received_ts=0):
    global lamport_clock

    with clock_lock:
        # Actualiza el reloj tomando el mayor valor entre
        # el reloj local y el recibido
        lamport_clock = max(lamport_clock, received_ts) + 1

        return lamport_clock


# Clase principal del servicio gRPC
class MessagingServiceServicer(messaging_pb2_grpc.MessagingServiceServicer):

    # Método remoto invocado por el cliente
    def SendMessage(self, request, context):

        try:
            # Actualiza el timestamp lógico
            ts = update_clock(request.timestamp)

            # Muestra información del mensaje recibido
            print(
                f"[gRPC SERVER] sender={request.sender} | "
                f"LT={ts} | msg='{request.message}'"
            )

            # Retorna respuesta al cliente
            return messaging_pb2.MessageResponse(
                sender="server",
                timestamp=ts,
                status="OK"
            )

        except Exception as e:

            # Muestra error en consola
            print(f"[ERROR SERVER] {e}")

            # Retorna mensaje de error al cliente
            return messaging_pb2.MessageResponse(
                sender="server",
                timestamp=lamport_clock,
                status="ERROR"
            )


# Función principal para iniciar el servidor
def serve(host="127.0.0.1", port=5002):

    try:
        # Crea servidor gRPC con soporte multihilo
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10)
        )

        # Registra el servicio en el servidor
        messaging_pb2_grpc.add_MessagingServiceServicer_to_server(
            MessagingServiceServicer(),
            server
        )

        # Define dirección y puerto del servidor
        server.add_insecure_port(f"{host}:{port}")

        # Inicia el servidor
        server.start()

        print(f"[gRPC SERVER] Escuchando en {host}:{port}")

        # Mantiene el servidor activo
        server.wait_for_termination()

    except Exception as e:

        # Captura errores generales del servidor
        print(f"[ERROR GENERAL SERVER] {e}")


# Punto de entrada principal del programa
if __name__ == "__main__":
    serve()