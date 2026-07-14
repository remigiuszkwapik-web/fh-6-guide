"""
dump.py — Diagnose: schlüsselt EIN Telemetriepaket komplett auf.

Zweck: Wenn Forza (z.B. FH6) ein anderes Byte-Layout hat als erwartet, zeigt dieses
Tool für JEDEN 4-Byte-Offset den Wert als float UND als int. Anhand bekannter
Referenzwerte (Auto steht still: Speed≈0, Drehzahl≈Leerlauf) lassen sich die echten
Positionen der Felder ablesen.

Aufruf:   python dump.py 20066    (Port anpassen)

Bedienung: Tool starten, dann im Spiel das Auto RUHIG STEHEN lassen (Motor an,
nicht fahren, kein Gas). Das Tool fängt das erste "aktive" Paket und druckt die
komplette Tabelle. Diese Ausgabe komplett kopieren und dem Ingenieur schicken.
"""

import socket
import struct
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5300

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
print(f"dump.py lauscht auf Port {PORT}.")
print("Lass das Auto im Spiel STILL STEHEN (Motor an, kein Gas), dann warte kurz …\n")

while True:
    data, _ = sock.recvfrom(4096)
    size = len(data)
    is_race = struct.unpack_from("<i", data, 0)[0]
    if is_race != 1:
        continue  # auf aktives Fahrzeug/Spiel warten

    print(f"===== PAKETGRÖSSE: {size} Bytes =====")
    print("offset |        float |          int32 |  uint16@ |  bytes")
    print("-------+--------------+----------------+----------+--------")
    for off in range(0, size - 3, 4):
        f = struct.unpack_from("<f", data, off)[0]
        i = struct.unpack_from("<i", data, off)[0]
        u16 = struct.unpack_from("<H", data, off)[0]
        b = data[off:off + 4].hex()
        # float lesbar formatieren (sehr große/kleine Zahlen abkürzen)
        fs = f"{f:12.4g}" if abs(f) < 1e9 else f"{f:12.3e}"
        print(f"{off:6d} | {fs} | {i:14d} | {u16:8d} | {b}")
    # letzte 1-3 Bytes (falls Größe nicht durch 4 teilbar)
    rest = size % 4
    if rest:
        print(f"(+{rest} Rest-Byte(s) am Ende: {data[size-rest:].hex()})")
    print("\n===== ENDE — diese Tabelle komplett kopieren =====")
    break
