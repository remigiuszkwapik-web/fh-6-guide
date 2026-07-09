"""
forza_format.py — Parser für das Forza "Data Out" Telemetrieformat.

Zentrale Idee: Ein UDP-Paket ist ein Byte-Block. Jedes Feld liegt an einem festen
BYTE-OFFSET und hat einen Typ (f32 = 4-Byte-Float, s32/u32 = 4-Byte-Ganzzahl,
u16/u8/s8 = kleiner). Alles little-endian ("<" in struct).

Die Offsets unten entsprechen dem etablierten FM7/FH4/FH5-"Dash"-Format. Der
gemeinsame Prefix (Byte 0..310) ist über alle Forza-Titel stabil; FH5 hängt am
Ende noch TireWear + TrackOrdinal an (Paket = 331 Bytes statt 311).

>>> FH6-VERIFIKATION <<<
Sollte FH6 die Offsets verschoben haben, erkennst du das am Sanity-Check (unten):
IsRaceOn muss 0/1 sein, RPM/Speed müssen plausibel sein. Passt das nicht, stimmt
das Format nicht — dann diese Offset-Tabelle an die echten Werte anpassen. Genau
dafür ist alles hier in EINER Tabelle gekapselt.
"""

import struct

# ─────────────────────────────────────────────────────────────────────────────
# Feldtabelle: (Name, Offset in Bytes, struct-Format).
# struct-Codes: i=s32, I=u32, f=f32, H=u16, B=u8, b=s8.  Alle little-endian.
# ─────────────────────────────────────────────────────────────────────────────
_WHEELS = ("FL", "FR", "RL", "RR")  # Reihenfolge in Forza: immer vorne-l, vorne-r, hinten-l, hinten-r


def _wheel_fields(base_name, start_offset, code="f", size=4):
    """Erzeugt die 4 Rad-Felder (…FL/FR/RL/RR) ab start_offset."""
    return [(f"{base_name}{w}", start_offset + i * size, code) for i, w in enumerate(_WHEELS)]


# Teil A — "Sled" (Byte 0..231): Physik-Grunddaten
FIELDS = [
    ("IsRaceOn", 0, "i"),
    ("TimestampMS", 4, "I"),
    ("EngineMaxRpm", 8, "f"),
    ("EngineIdleRpm", 12, "f"),
    ("CurrentEngineRpm", 16, "f"),
    ("AccelerationX", 20, "f"), ("AccelerationY", 24, "f"), ("AccelerationZ", 28, "f"),
    ("VelocityX", 32, "f"), ("VelocityY", 36, "f"), ("VelocityZ", 40, "f"),
    ("AngularVelocityX", 44, "f"), ("AngularVelocityY", 48, "f"), ("AngularVelocityZ", 52, "f"),
    ("Yaw", 56, "f"), ("Pitch", 60, "f"), ("Roll", 64, "f"),
    *_wheel_fields("NormSuspTravel", 68),
    *_wheel_fields("TireSlipRatio", 84),
    *_wheel_fields("WheelRotSpeed", 100),
    *_wheel_fields("WheelOnRumble", 116),
    *_wheel_fields("WheelInPuddle", 132),
    *_wheel_fields("SurfaceRumble", 148),
    *_wheel_fields("TireSlipAngle", 164),
    *_wheel_fields("TireCombinedSlip", 180),
    *_wheel_fields("SuspTravelMeters", 196),
    ("CarOrdinal", 212, "i"),
    ("CarClass", 216, "i"),
    ("CarPerformanceIndex", 220, "i"),
    ("DrivetrainType", 224, "i"),   # 0=FWD, 1=RWD, 2=AWD
    ("NumCylinders", 228, "i"),
    # Teil B — "Dash" (ab Byte 232): erweiterte Daten
    ("PositionX", 232, "f"), ("PositionY", 236, "f"), ("PositionZ", 240, "f"),
    ("Speed", 244, "f"),      # m/s
    ("Power", 248, "f"),      # W
    ("Torque", 252, "f"),     # Nm
    *_wheel_fields("TireTemp", 256),  # °F
    ("Boost", 272, "f"),
    ("Fuel", 276, "f"),
    ("DistanceTraveled", 280, "f"),
    ("BestLap", 284, "f"), ("LastLap", 288, "f"),
    ("CurrentLap", 292, "f"), ("CurrentRaceTime", 296, "f"),
    ("LapNumber", 300, "H"),
    ("RacePosition", 302, "B"),
    ("Accel", 303, "B"), ("Brake", 304, "B"), ("Clutch", 305, "B"),
    ("HandBrake", 306, "B"), ("Gear", 307, "B"),
    ("Steer", 308, "b"),
    ("NormalizedDrivingLine", 309, "b"),
    ("NormalizedAIBrakeDifference", 310, "b"),
    # Teil C — nur FH5 (Paket 331 Bytes): am Ende angehängt
    *_wheel_fields("TireWear", 311),
    ("TrackOrdinal", 327, "i"),
]

# Bekannte Paketgrößen → Formatname (zur Diagnose)
KNOWN_SIZES = {
    232: "Sled (V1, keine Reifentemps/Runden!)",
    311: "Dash (V2, FM7/FH4)",
    331: "Dash (V2, FH5 inkl. TireWear/TrackOrdinal)",
}


def parse(packet: bytes) -> dict:
    """
    Wandelt ein rohes UDP-Paket in ein Dict {Feldname: Wert}.
    Felder, die über das Paketende hinausgehen (z.B. TireTemp bei einem 232-Byte
    Sled-Paket), werden übersprungen — so bleibt der Parser robust gegen kürzere
    Formate.
    """
    n = len(packet)
    out = {"_bytes": n}
    for name, offset, code in FIELDS:
        end = offset + struct.calcsize("<" + code)
        if end > n:
            continue  # Feld nicht im Paket enthalten (kürzeres Format)
        (value,) = struct.unpack_from("<" + code, packet, offset)
        out[name] = value
    return out


def sanity_check(sample: dict) -> list:
    """
    Prüft ein geparstes Paket auf Plausibilität. Gibt eine Liste von Warnungen
    zurück (leer = alles gut). Nützlich, um falsche Byte-Offsets sofort zu erkennen,
    falls FH6 das Format geändert hat.
    """
    warns = []
    race = sample.get("IsRaceOn")
    if race not in (0, 1):
        warns.append(f"IsRaceOn={race} (erwartet 0 oder 1) → Offsets stimmen vermutlich nicht!")
    rpm = sample.get("CurrentEngineRpm")
    if rpm is not None and not (0 <= rpm <= 20000):
        warns.append(f"CurrentEngineRpm={rpm:.0f} unplausibel (erwartet 0..20000).")
    mx = sample.get("EngineMaxRpm")
    if mx is not None and not (0 <= mx <= 20000):
        warns.append(f"EngineMaxRpm={mx:.0f} unplausibel.")
    dt = sample.get("DrivetrainType")
    if dt is not None and dt not in (0, 1, 2):
        warns.append(f"DrivetrainType={dt} (erwartet 0/1/2).")
    return warns


# Kleine Helfer für Einheiten-Umrechnung, damit Anzeigen menschlich sind
def mps_to_kmh(mps: float) -> float:
    return mps * 3.6


def f_to_c(fahrenheit: float) -> float:
    return (fahrenheit - 32.0) * 5.0 / 9.0


DRIVETRAIN_NAMES = {0: "FWD", 1: "RWD", 2: "AWD"}


def driven_wheels(drivetrain_type: int):
    """Gibt die Namen der angetriebenen Räder zurück (für Traktionsanalyse)."""
    if drivetrain_type == 0:      # FWD
        return ("FL", "FR")
    if drivetrain_type == 1:      # RWD
        return ("RL", "RR")
    return _WHEELS                # AWD: alle
