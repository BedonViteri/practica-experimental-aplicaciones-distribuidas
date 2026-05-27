# Práctica Experimental U1 — Aplicaciones Distribuidas

## Descripción
Implementación y comparación de comunicación entre procesos distribuidos:
TCP Sockets vs gRPC con relojes lógicos de Lamport en un sistema de tres nodos.

## Integrantes
- Bedón Keyla 
- Emanuel Juliana 
- Viñueza Harold 
- Castro Pedro 

## Requisitos
- Python 3.13.7
- pip install grpcio grpcio-tools protobuf pandas matplotlib

## Estructura

practica-experimental-aplicaciones-distribuidas/
├── src/
│   ├── sockets/
│   │   ├── server.py
│   │   ├── client.py
│   │   ├── client2.py
│   │   └── client3.py
│   └── grpc/
│       ├── messaging.proto
│       ├── server_grpc.py
│       └── client_grpc.py
├── data/
│   ├── latency_sockets.csv
│   ├── latency_grpc.csv
│   └── exchanges_node1.json
├── docs/
│   └── figures/
│       └── boxplot.png
├── analisis.py
└── README.md

## Ejecución

### Paso 1 — Instalar dependencias
pip install grpcio grpcio-tools protobuf pandas matplotlib

### Paso 2 — TCP Sockets (3 nodos)
Terminal 1 (servidor):
python src/sockets/server.py

Terminal 2 (nodo 1):
python src/sockets/client.py

Terminal 3 (nodo 2):
python src/sockets/client2.py

Terminal 4 (nodo 3):
python src/sockets/client3.py

### Paso 3 — Compilar proto gRPC
python -m grpc_tools.protoc -I src/grpc --python_out=src/grpc --grpc_python_out=src/grpc src/grpc/messaging.proto

### Paso 4 — gRPC
Terminal 1 (servidor):
python src/grpc/server_grpc.py

Terminal 2 (cliente):
python src/grpc/client_grpc.py

### Paso 5 — Análisis estadístico
python analisis.py

## Resultados
| Métrica    | TCP Sockets | gRPC     |
|------------|-------------|----------|
| Media      | 0.688 ms    | 1.120 ms |
| Mediana    | 0.672 ms    | 1.064 ms |
| Std Dev    | 0.099 ms    | 0.248 ms |
| Mínimo     | 0.527 ms    | 0.788 ms |
| P95        | 0.885 ms    | 1.538 ms |
| IQR        | 0.120 ms    | 0.253 ms |
| Máximo     | 1.078 ms    | 2.287 ms |

TCP fue 38.6% más rápido y mostró variabilidad 2.51× menor que gRPC.
La invariante causal de Lamport se cumplió en el 100% de los 200 intercambios.
