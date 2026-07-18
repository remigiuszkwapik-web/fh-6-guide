"""
repeater.py — Forza Data Out an MEHRERE Empfänger verteilen (Fan-out).

Forza hat nur EIN Data-Out-Ziel. Wer gleichzeitig z.B. co-driver UND MOZA Pit
House füttern will, schickt Forza an dieses Skript, das jedes Paket an mehrere
Ziele weiterreicht:

    FH6 Data Out ──► repeater ──►┬──► co-driver   (127.0.0.1:5300)
                                 └──► MOZA Pithouse (127.0.0.1:20066)

Aufruf (Standardwerte unten):
    python repeater.py
    python repeater.py 5959 127.0.0.1:5300 127.0.0.1:20066   # eigener Eingangs-Port + Ziele

Danach in FH6: Data Out IP = deine LAN-IP, Port = LISTEN_PORT (unten, Standard 5959).
WICHTIG: LISTEN_PORT muss sich von allen Ziel-Ports unterscheiden (5300, 20066 sind
schon von co-driver bzw. Pit House belegt).
"""

import socket
import sys

# ── Standard-Konfiguration (per Kommandozeile überschreibbar) ────────────────
LISTEN_PORT = 5959                       # hierhin schickt Forza (Data Out Port)
TARGETS = [
    ("127.0.0.1", 5300),                 # co-driver
    ("127.0.0.1", 20066)                 # MOZA Pit House
]

# Optional per Argumenten: repeater.py <listen_port> <host:port> <host:port> ...
if len(sys.argv) > 1:
    LISTEN_PORT = int(sys.argv[1])
if len(sys.argv) > 2:
    TARGETS = []
    for t in sys.argv[2:]:
        host, port = t.rsplit(":", 1)
        TARGETS.append((host, int(port)))

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("0.0.0.0", LISTEN_PORT))
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

targets_str = ", ".join(f"{h}:{p}" for h, p in TARGETS)
print(f"Repeater lauscht auf UDP {LISTEN_PORT} → verteilt an: {targets_str}")
print(f"In FH6: Data Out IP = deine LAN-IP, Port = {LISTEN_PORT}. (Strg+C zum Beenden)\n")

count = 0
try:
    while True:
        data, _ = rx.recvfrom(2048)
        for target in TARGETS:
            tx.sendto(data, target)
        count += 1
        if count % 300 == 0:                       # ~alle 5 s ein Lebenszeichen
            print(f"  … {count} Pakete verteilt", end="\r")
except KeyboardInterrupt:
    print(f"\nBeendet. {count} Pakete verteilt.")
