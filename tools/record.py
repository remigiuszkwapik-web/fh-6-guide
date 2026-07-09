"""
record.py — Zeichnet eine Fahrsession als CSV auf.

Aufruf:
    python record.py                          -> schreibt session.csv, Port 5300
    python record.py --out goliath.csv        -> eigener Dateiname
    python record.py --port 5300 --raceonly   -> nur Pakete mit IsRaceOn==1 speichern

Ablauf: 2 saubere Runden fahren, dann mit Strg+C beenden. Danach die CSV mit
debrief.py auswerten.

Es werden nur die für die Analyse relevanten Felder gespeichert (nicht der ganze
Paketinhalt), damit die CSV übersichtlich bleibt.
"""

import argparse
import csv
import socket
import sys
import time

import forza_format as ff

# Diese Felder landen in der CSV (eine Spalte je Eintrag).
RECORD_FIELDS = [
    "TimestampMS", "IsRaceOn", "CurrentRaceTime", "LapNumber", "CurrentLap",
    "Speed", "CurrentEngineRpm", "EngineMaxRpm", "Gear",
    "Accel", "Brake", "Steer", "HandBrake",
    "AccelerationX", "AccelerationY", "AccelerationZ",
    "AngularVelocityY",
    "DrivetrainType", "CarPerformanceIndex", "CarClass",
    # Rad-Felder
    *[f"NormSuspTravel{w}" for w in ("FL", "FR", "RL", "RR")],
    *[f"TireSlipRatio{w}" for w in ("FL", "FR", "RL", "RR")],
    *[f"TireSlipAngle{w}" for w in ("FL", "FR", "RL", "RR")],
    *[f"WheelRotSpeed{w}" for w in ("FL", "FR", "RL", "RR")],
    *[f"TireTemp{w}" for w in ("FL", "FR", "RL", "RR")],
]


def main():
    ap = argparse.ArgumentParser(description="FH6 Telemetrie-Recorder")
    ap.add_argument("--out", default="session.csv", help="Ziel-CSV (default: session.csv)")
    ap.add_argument("--port", type=int, default=5300, help="UDP-Port (default: 5300)")
    ap.add_argument("--raceonly", action="store_true",
                    help="Nur Pakete mit IsRaceOn==1 speichern")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))
    print(f"Recorder lauscht auf Port {args.port} → schreibt {args.out}")
    print("Fahr deine 2 sauberen Runden. Strg+C zum Beenden.\n")

    written = 0
    first_checked = False
    start = time.time()
    try:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=RECORD_FIELDS, extrasaction="ignore")
            writer.writeheader()
            while True:
                data, _ = sock.recvfrom(2048)
                s = ff.parse(data)

                if not first_checked:
                    size = s["_bytes"]
                    fmt = ff.KNOWN_SIZES.get(size, "UNBEKANNT — Offsets prüfen (docs/01)!")
                    print(f"Format: {size} Bytes ({fmt})")
                    for w in ff.sanity_check(s):
                        print("  ⚠️  " + w)
                    first_checked = True

                if args.raceonly and s.get("IsRaceOn") != 1:
                    continue

                writer.writerow(s)
                written += 1
                if written % 120 == 0:  # ~alle 2 s ein Lebenszeichen
                    print(f"  … {written} Zeilen aufgezeichnet", end="\r")
    except KeyboardInterrupt:
        dur = time.time() - start
        print(f"\nFertig: {written} Zeilen in {dur:.0f}s → {args.out}")
        print(f"Jetzt auswerten:  python debrief.py {args.out}")


if __name__ == "__main__":
    main()
