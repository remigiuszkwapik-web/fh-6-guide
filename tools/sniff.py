"""
sniff.py — Schnelltest: Kommen Data-Out-Pakete an, und stimmt das Format?

Aufruf:   python sniff.py            (Port 5300)
          python sniff.py 5300       (anderer Port)

Was es tut: lauscht auf dem UDP-Port, und sobald du im Spiel FÄHRST, zeigt es
für jedes ~20. Paket die Größe + ein paar geparste Kernwerte an. So siehst du in
einem Test zweierlei:
  1) ob überhaupt Daten ankommen, und
  2) ob die Byte-Offsets stimmen (IsRaceOn=0/1, plausible RPM/Speed/Gang).

Notiere dir die BYTE-ZAHL — sie identifiziert das Format (siehe docs/01).
"""

import socket
import sys

import forza_format as ff

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5300

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
print(f"Lausche auf UDP-Port {PORT}. Starte im Spiel ein Rennen und fahr los …")
print("(Strg+C zum Beenden)\n")

count = 0
warned = False
try:
    while True:
        data, addr = sock.recvfrom(2048)
        count += 1
        if count == 1:
            size = len(data)
            fmt = ff.KNOWN_SIZES.get(size, "UNBEKANNT — evtl. FH6-Formatänderung, Offsets prüfen!")
            print(f"Erstes Paket: {size} Bytes von {addr}  →  Format: {fmt}\n")

        if count % 20 != 0:   # nur jedes 20. Paket ausgeben, sonst zu viel
            continue

        s = ff.parse(data)

        if not warned:
            for w in ff.sanity_check(s):
                print("  ⚠️  " + w)
            warned = True  # nur einmal warnen

        race = s.get("IsRaceOn")
        if race != 1:
            print(f"[#{count}] IsRaceOn={race} — kein aktives Rennen (Menü/Pause), Werte ignorieren.")
            continue

        speed = ff.mps_to_kmh(s.get("Speed", 0.0))
        rpm = s.get("CurrentEngineRpm", 0.0)
        gear = s.get("Gear", "?")
        dt = ff.DRIVETRAIN_NAMES.get(s.get("DrivetrainType"), "?")
        tt = [s.get(f"TireTemp{w}") for w in ("FL", "FR", "RL", "RR")]
        tt_c = "  ".join(f"{ff.f_to_c(t):.0f}°C" if t is not None else "—" for t in tt)
        print(f"[#{count}] {speed:5.0f} km/h  {rpm:5.0f} rpm  Gang {gear}  {dt}  Reifen[{tt_c}]")

except KeyboardInterrupt:
    print(f"\nBeendet. {count} Pakete empfangen.")
