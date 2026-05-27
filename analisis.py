import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

tcp = pd.read_csv('data/latency_sockets.csv')['latency_ms']
grpc = pd.read_csv('data/latency_grpc.csv')['latency_ms']

for nombre, datos in [('TCP Sockets', tcp), ('gRPC', grpc)]:
    print(f"{nombre}:")
    print(f"  Media:    {datos.mean():.3f} ms")
    print(f"  Mediana:  {datos.median():.3f} ms")
    print(f"  Std Dev:  {datos.std():.3f} ms")
    print(f"  P95:      {np.percentile(datos, 95):.3f} ms")
    print(f"  Min:      {datos.min():.3f} ms")
    print(f"  Max:      {datos.max():.3f} ms")

fig, ax = plt.subplots(figsize=(7, 5))
bp = ax.boxplot([tcp, grpc], tick_labels=['TCP Sockets', 'gRPC'],
                patch_artist=True,
                medianprops=dict(color='red', linewidth=2))
bp['boxes'][0].set_facecolor('#4472C4')
bp['boxes'][0].set_alpha(0.75)
bp['boxes'][1].set_facecolor('#ED7D31')
bp['boxes'][1].set_alpha(0.75)
ax.set_ylabel('Latencia (ms)', fontsize=12)
ax.set_title('Comparacion de Latencia: TCP Sockets vs gRPC\n(n=100 envios)', fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('docs/boxplot.png', dpi=300)
print("\nBoxplot guardado en docs/boxplot.png")

# Tabla comparativa - Castro Lopez Pedro
tabla = [
    ["Protocolo base",       "TCP directo",                "HTTP/2 sobre TCP"],
    ["Serializacion",        "JSON / texto plano",         "Protocol Buffers (binario)"],
    ["Latencia promedio",    f"{tcp.mean():.3f} ms",       f"{grpc.mean():.3f} ms"],
    ["Desv. estandar",       f"{tcp.std():.3f} ms",        f"{grpc.std():.3f} ms"],
    ["Percentil 95",         f"{np.percentile(tcp,95):.3f} ms", f"{np.percentile(grpc,95):.3f} ms"],
    ["Overhead conexion",    "Bajo",                       "Medio (HTTP/2)"],
    ["Tipado de mensajes",   "No (manual)",                "Si (schema .proto)"],
    ["Streaming nativo",     "No",                         "Si (4 modos)"],
    ["Uso recomendado",      "IoT, baja latencia",         "Microservicios, APIs internas"],
]

print("\n═══════ TABLA COMPARATIVA TCP SOCKETS vs gRPC ═══════")
print(tabulate(tabla, headers=["Caracteristica", "TCP Sockets", "gRPC"], tablefmt="fancy_grid"))