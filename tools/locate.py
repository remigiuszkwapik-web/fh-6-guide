"""
locate.py — Verortet Ereignisse auf der Strecke und urteilt: Fahrfehler oder Setup?

Aufruf:
    python locate.py fahrt.csv

Nutzt die Weltposition (PositionX/Z), die die AKTUELLE record.py mitschneidet.
Es:
  · findet DREHER (starke Gierrate) und verortet jeden (Zeit, Runde, Koordinaten),
  · prüft den Kontext jedes Drehers (kalte Reifen? Vollgas? an einer Traktions-Problemstelle?),
  · findet HÄUFUNGSPUNKTE von Rad-Durchdrehen (Raster über die Strecke),
  · gibt pro Dreher ein Urteil: eher Fahrfehler oder eher Setup/streckenspezifisch.

Ältere CSVs ohne PositionX/Z funktionieren nur eingeschränkt (ohne Verortung).
"""

import argparse
import csv
import math
import statistics as st

import forza_format as ff

SPIN_YAW = 1.5        # rad/s: Gierrate darüber = Dreh-/Ausbrechereignis (normale Kurve << 1.0)
FULL_THROTTLE = 180   # Accel (0..255) darüber = "unter Gas"
COLD_TIRE_C = 60.0    # Hinterreifen darunter = kalt (wenig Grip)
GRID_M = 25.0         # Rasterzelle in Metern für Häufungspunkte
SPIN_DEBOUNCE_S = 1.5 # Mindestabstand zwischen zwei gezählten Drehern


def fnum(row, key, default=0.0):
    try:
        return float(row.get(key, ""))
    except (TypeError, ValueError):
        return default


def has_position(rows):
    return any(r.get("PositionX") not in (None, "") for r in rows)


def cell(x, z):
    return (round(x / GRID_M), round(z / GRID_M))


def analyze(rows):
    rows = [r for r in rows if int(fnum(r, "IsRaceOn")) == 1]
    if not rows:
        return None
    pos = has_position(rows)

    # Zeitachse (s) je Sample
    t0 = fnum(rows[0], "TimestampMS")

    def tsec(r):
        return (fnum(r, "TimestampMS") - t0) / 1000.0

    # --- Rad-Durchdrehen je Rasterzelle (Häufungspunkte) ---
    spin_cells = {}
    if pos:
        for r in rows:
            if fnum(r, "Accel") <= FULL_THROTTLE:
                continue
            driven = ff.driven_wheels(int(fnum(r, "DrivetrainType")))
            if any(fnum(r, f"TireSlipRatio{w}") > 0.2 for w in driven):
                c = cell(fnum(r, "PositionX"), fnum(r, "PositionZ"))
                spin_cells[c] = spin_cells.get(c, 0) + 1
    # Top-Häufungspunkte (Zellen mit den meisten Durchdreh-Samples)
    hotspots = sorted(spin_cells.items(), key=lambda kv: kv[1], reverse=True)
    hot_set = {c for c, n in hotspots if n >= 8}   # "problematische" Stellen

    # --- Dreher finden (Gierrate) ---
    spins = []
    last_t = -999.0
    for i, r in enumerate(rows):
        yaw = abs(fnum(r, "AngularVelocityY"))
        if yaw < SPIN_YAW:
            continue
        t = tsec(r)
        if t - last_t < SPIN_DEBOUNCE_S:
            continue   # gleicher Dreher, nicht doppelt zählen
        last_t = t
        rear_temp = (ff.f_to_c(fnum(r, "TireTempRL")) + ff.f_to_c(fnum(r, "TireTempRR"))) / 2
        # Gas kurz VOR dem Ereignis (bis zu ~0.3 s zurück)
        accel_before = max((fnum(rows[j], "Accel") for j in range(max(0, i - 18), i + 1)), default=0)
        c = cell(fnum(r, "PositionX"), fnum(r, "PositionZ")) if pos else None
        spins.append(dict(
            t=t, lap=int(fnum(r, "LapNumber")), yaw=yaw,
            speed=ff.mps_to_kmh(fnum(r, "Speed")),
            rear_temp=rear_temp, accel_before=accel_before,
            x=fnum(r, "PositionX"), z=fnum(r, "PositionZ"), cell=c,
            in_hotspot=(c in hot_set) if pos else False,
        ))

    return dict(pos=pos, spins=spins, hotspots=hotspots[:5], hot_set=hot_set,
                duration=tsec(rows[-1]))


def verdict(s):
    """Urteil pro Dreher: Fahrfehler vs. Setup."""
    cold = s["rear_temp"] < COLD_TIRE_C
    on_gas = s["accel_before"] > FULL_THROTTLE
    if cold and on_gas:
        return ("FAHRFEHLER (kalte Reifen)",
                f"Hinterreifen nur {s['rear_temp']:.0f}°C — unter Grip-Fenster. Erste Runde/kalt "
                "sanfter ans Gas, kein Setup-Thema.")
    if on_gas and s["in_hotspot"]:
        return ("SETUP/STELLE",
                "Genau hier dreht auch sonst regelmäßig das Rad durch (Häufungspunkt). Das Heck ist "
                "an dieser Stelle unter Gas systematisch marginal → mehr Traktion (Diff/Heck-Grip) "
                "oder bewusst sanfter aus dieser Kurve.")
    if on_gas:
        return ("EHER FAHRFEHLER",
                "Vollgas-Ausbruch, aber kein wiederkehrender Problempunkt → an dieser Stelle zu früh/"
                "zu viel Gas. Einzelfall, kein Setup-Muster.")
    return ("UNKLAR",
            "Kein klares Gas-Muster — evtl. Bremsen/Einlenken oder Randstein. Genauer ansehen.")


def report(a):
    if a is None:
        return "Keine auswertbaren Daten (IsRaceOn==1 fehlt)."
    L = ["# STRECKEN-VERORTUNG (FH6)", ""]
    if not a["pos"]:
        L.append("⚠️ Keine Positionsdaten in dieser CSV — mit der AKTUELLEN record.py neu aufnehmen, "
                 "dann kann ich Dreher verorten und Häufungspunkte finden.")
        L.append("")

    # Dreher
    L.append(f"## Dreher / starke Ausbrüche: {len(a['spins'])}")
    if not a["spins"]:
        L.append("- Keine erkannt. 👍")
    for k, s in enumerate(a["spins"], 1):
        v_title, v_text = verdict(s)
        loc = f"@ Pos ({s['x']:.0f}, {s['z']:.0f})" if a["pos"] else "(keine Position)"
        L.append(f"\n**Dreher {k}** — t={s['t']:.0f}s · Runde {s['lap']} · {s['speed']:.0f} km/h · "
                 f"Heck {s['rear_temp']:.0f}°C {loc}")
        L.append(f"→ **{v_title}**: {v_text}")
    L.append("")

    # Häufungspunkte Durchdrehen
    if a["pos"]:
        L.append("## Traktions-Häufungspunkte (wo dreht das Rad durch?)")
        if a["hotspots"]:
            for (cx, cz), n in a["hotspots"]:
                tag = "  ← Problemstelle" if (cx, cz) in a["hot_set"] else ""
                L.append(f"- Zone ({cx*GRID_M:.0f}, {cz*GRID_M:.0f}): {n} Durchdreh-Samples{tag}")
            L.append("  - Konzentriert sich das auf wenige Zonen → dort gezielt Traktion/Fahrweise. "
                     "Gleichmäßig verteilt → allgemeiner Grip/Fahrstil.")
        else:
            L.append("- Keine nennenswerten Durchdreh-Häufungen.")
    L.append("")
    L.append("---")
    L.append("*So dokumentierst du automatisch, WO es passiert ist — inkl. Urteil Fahrfehler/Setup.*")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="FH6 Ereignis-Verortung")
    ap.add_argument("csv")
    ap.add_argument("--out")
    args = ap.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    txt = report(analyze(rows))
    print(txt)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(txt)
        print(f"\n(gespeichert: {args.out})")


if __name__ == "__main__":
    main()
