"""
carinfo.py — Fahrzeug erkennen + Spec-Profil aus der Telemetrie ableiten.

Aufruf:
    python carinfo.py fahrt.csv
    python carinfo.py fahrt.csv --name "Maserati Ghibli Cup"   # Namen zur CarOrdinal merken

Jedes Forza-Auto hat eine eindeutige CarOrdinal (Fahrzeug-ID). Dieses Tool:
  · liest die ID aus der Aufnahme (nötig: mit aktueller record.py aufgenommen),
  · schlägt den Namen in cars.json nach (oder merkt ihn sich mit --name),
  · leitet aus den Daten ein Spec-Profil ab: Antrieb, Zylinder, Drehzahlband,
    Spitzenleistung & -drehmoment (inkl. Drehzahl), Topspeed, PI, Klasse.

So weiß der Ingenieur immer, WELCHES Auto vorliegt, und vermischt nie zwei Autos.
"""

import argparse
import csv
import json
import os
import statistics as st

import forza_format as ff

CARS_DB = os.path.join(os.path.dirname(__file__), "cars.json")


def load_db():
    if os.path.exists(CARS_DB):
        with open(CARS_DB, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_db(db):
    with open(CARS_DB, "w", encoding="utf-8") as fh:
        json.dump(db, fh, ensure_ascii=False, indent=2, sort_keys=True)


def pi_class(pi):
    """Klassenbuchstabe aus dem Performance-Index (Forza-Bereiche)."""
    if pi <= 500:
        return "D"
    if pi <= 600:
        return "C"
    if pi <= 700:
        return "B"
    if pi <= 800:
        return "A"
    if pi <= 900:
        return "S1"
    if pi <= 998:
        return "S2"
    return "X"


def fnum(row, key, default=0.0):
    try:
        return float(row.get(key, ""))
    except (TypeError, ValueError):
        return default


def profile(rows):
    rows = [r for r in rows if int(fnum(r, "IsRaceOn")) == 1]
    if not rows:
        return None
    r0 = rows[0]
    ordinal = int(fnum(r0, "CarOrdinal")) if r0.get("CarOrdinal") not in (None, "") else None

    # Spitzenleistung / -drehmoment inkl. Drehzahl (aus allen Samples)
    def peak(field):
        best_v, best_rpm = 0.0, 0.0
        for r in rows:
            v = fnum(r, field)
            if v > best_v:
                best_v, best_rpm = v, fnum(r, "CurrentEngineRpm")
        return best_v, best_rpm

    have_power = any(r.get("Power") for r in rows)
    p_w, p_rpm = peak("Power") if have_power else (0.0, 0.0)
    t_nm, t_rpm = peak("Torque") if any(r.get("Torque") for r in rows) else (0.0, 0.0)

    return dict(
        ordinal=ordinal,
        drivetrain=ff.DRIVETRAIN_NAMES.get(int(fnum(r0, "DrivetrainType")), "?"),
        cylinders=int(fnum(r0, "NumCylinders")) if r0.get("NumCylinders") else None,
        pi=int(fnum(r0, "CarPerformanceIndex")),
        rpm_idle=fnum(r0, "EngineIdleRpm"),
        rpm_max=max(fnum(r, "EngineMaxRpm") for r in rows),
        power_kw=p_w / 1000.0, power_rpm=p_rpm,
        power_ps=p_w / 1000.0 * 1.35962,
        torque_nm=t_nm, torque_rpm=t_rpm,
        top_speed=ff.mps_to_kmh(max(fnum(r, "Speed") for r in rows)),
    )


def report(rows, name_arg=None):
    p = profile(rows)
    if p is None:
        return "Keine auswertbaren Daten."
    db = load_db()

    # Namen merken/nachschlagen
    name = None
    if p["ordinal"] is not None:
        key = str(p["ordinal"])
        if name_arg:
            db[key] = name_arg
            save_db(db)
            name = name_arg
        else:
            name = db.get(key)

    L = ["# FAHRZEUG-PROFIL (aus Telemetrie)", ""]
    if p["ordinal"] is None:
        L.append("⚠️ Keine CarOrdinal in dieser CSV (mit AKTUELLER record.py neu aufnehmen, "
                 "dann Auto-Erkennung).")
        ident = "unbekannt"
    else:
        ident = f"{name} " if name else ""
        ident += f"(ID {p['ordinal']})"
        if not name:
            L.append('ℹ️ Auto noch ohne Namen. Einmalig setzen:  '
                     'python carinfo.py <csv> --name "Maserati Ghibli Cup"')
    L.append(f"**Auto:** {ident}")
    L.append(f"**Klasse/PI:** {pi_class(p['pi'])} {p['pi']} · **Antrieb:** {p['drivetrain']}"
             + (f" · **Zylinder:** {p['cylinders']}" if p['cylinders'] else ""))
    L.append(f"**Drehzahl:** Leerlauf {p['rpm_idle']:.0f} · Begrenzer {p['rpm_max']:.0f} rpm")
    if p["power_kw"] > 0:
        L.append(f"**Leistung (gemessen):** ~{p['power_ps']:.0f} PS ({p['power_kw']:.0f} kW) "
                 f"@ {p['power_rpm']:.0f} rpm")
    if p["torque_nm"] > 0:
        L.append(f"**Drehmoment (gemessen):** ~{p['torque_nm']:.0f} Nm @ {p['torque_rpm']:.0f} rpm")
    L.append(f"**Topspeed (gesehen):** {p['top_speed']:.0f} km/h")
    L.append("")
    L.append("_'gemessen' = aus deiner Fahrt abgeleitet, nicht aus einer Datenbank._")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="FH6 Fahrzeug-Erkennung & Profil")
    ap.add_argument("csv")
    ap.add_argument("--name", help='Auto-Name zur CarOrdinal merken, z. B. --name "Maserati Ghibli Cup"')
    args = ap.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    print(report(rows, args.name))


if __name__ == "__main__":
    main()
