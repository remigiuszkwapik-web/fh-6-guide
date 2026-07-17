"""
gearing.py — Getriebe-Analyse aus einer Aufnahme (CSV von record.py).

Aufruf:
    python gearing.py fahrt.csv

Beantwortet die Ingenieurs-Getriebefragen:
  · Wo liegt die Peak-Power-Drehzahl? (aus den Daten geschätzt, wenn Power vorhanden)
  · Triffst du den Begrenzer (Gänge/Achse zu kurz) oder bleibt Topspeed liegen (zu lang)?
  · Fällt die Drehzahl beim Hochschalten unter das Powerband (Gänge zu weit gespreizt)?
  · Bist du am Kurvenausgang im kräftigen Drehzahlbereich?

Voraussetzung für die Leistungskurve: mit der AKTUELLEN record.py aufnehmen
(sie schneidet Power/Torque/EngineIdleRpm mit). Ältere CSVs ohne diese Spalten
funktionieren auch, nur ohne Peak-Power-Schätzung.
"""

import argparse
import csv
import statistics as st

import forza_format as ff

FULL_THROTTLE = 200   # Accel (0..255) darüber = "unter Vollgas"
LIMITER_FRAC = 0.985  # RPM ab diesem Anteil von Max = am Begrenzer


def fnum(row, key, default=0.0):
    try:
        return float(row.get(key, ""))
    except (TypeError, ValueError):
        return default


def estimate_peak_power_rpm(rows, rpm_max):
    """Schätzt die Drehzahl der maximalen Leistung, indem Power über RPM gemittelt wird."""
    if not any(r.get("Power") for r in rows):
        return None
    bin_w = max(100.0, rpm_max / 40.0)         # ~40 Klassen über den Drehzahlbereich
    bins = {}
    for r in rows:
        p = fnum(r, "Power")
        rpm = fnum(r, "CurrentEngineRpm")
        if p <= 0 or rpm <= 0:
            continue
        b = round(rpm / bin_w) * bin_w
        bins.setdefault(b, []).append(p)
    if not bins:
        return None
    # nur Klassen mit genug Messwerten, damit Ausreißer nicht gewinnen
    scored = [(st.mean(v), b) for b, v in bins.items() if len(v) >= 5]
    if not scored:
        return None
    return max(scored)[1]


def analyze(rows):
    rows = [r for r in rows if int(fnum(r, "IsRaceOn")) == 1]
    if not rows:
        return None

    rpm_max = max(fnum(r, "EngineMaxRpm") for r in rows)
    rpm_idle = min((fnum(r, "EngineIdleRpm") for r in rows if r.get("EngineIdleRpm")), default=0.0)
    peak_power_rpm = estimate_peak_power_rpm(rows, rpm_max)
    # Ziel-Schaltdrehzahl: nahe Begrenzer; Fallback wenn keine Power-Daten
    shift_target = rpm_max * 0.97

    # Höchstgeschwindigkeit + Zustand dort
    top = max(rows, key=lambda r: fnum(r, "Speed"))
    top_speed = ff.mps_to_kmh(fnum(top, "Speed"))
    top_gear = int(fnum(top, "Gear"))
    top_rpm = fnum(top, "CurrentEngineRpm")

    # Begrenzer-Treffer je Gang (steigende Flanken unter Vollgas)
    limiter = {}
    prev_hit = False
    for r in rows:
        hit = (fnum(r, "Accel") > FULL_THROTTLE and
               fnum(r, "CurrentEngineRpm") >= LIMITER_FRAC * rpm_max)
        if hit and not prev_hit:
            g = int(fnum(r, "Gear"))
            limiter[g] = limiter.get(g, 0) + 1
        prev_hit = hit

    # Hochschalt-Drehzahlabfall: RPM kurz vor vs. kurz nach dem Hochschalten.
    # Forza zeigt beim Schalten kurz Gang 11 (= Leerlauf); wir überspringen ihn und
    # erkennen den Wechsel vom letzten "echten" Gang auf den nächsthöheren.
    NEUTRAL = 11
    upshifts = {}   # gang_von -> Liste (rpm_vor, rpm_nach)
    last_real, last_idx = None, None
    for i, r in enumerate(rows):
        g = int(fnum(r, "Gear"))
        if g == NEUTRAL or g <= 0:
            continue
        if last_real is not None and g == last_real + 1:
            rpm_before = fnum(rows[last_idx], "CurrentEngineRpm")
            rpm_after = fnum(rows[min(i + 5, len(rows) - 1)], "CurrentEngineRpm")
            if rpm_before > 0 and rpm_after > 0:
                upshifts.setdefault(last_real, []).append((rpm_before, rpm_after))
        last_real, last_idx = g, i

    # Kurvenausgang-Drehzahl: Moment, in dem nach einer Kurve Vollgas kommt
    exit_rpms = []
    for i in range(1, len(rows)):
        was_part = fnum(rows[i - 1], "Accel") <= FULL_THROTTLE
        now_full = fnum(rows[i], "Accel") > FULL_THROTTLE
        cornering = abs(fnum(rows[i], "AccelerationX")) > 2.0
        if was_part and now_full and cornering:
            exit_rpms.append(fnum(rows[i], "CurrentEngineRpm"))

    return dict(
        rpm_max=rpm_max, rpm_idle=rpm_idle, peak_power_rpm=peak_power_rpm,
        shift_target=shift_target, top_speed=top_speed, top_gear=top_gear, top_rpm=top_rpm,
        limiter=limiter, upshifts=upshifts,
        exit_rpm=(st.mean(exit_rpms) if exit_rpms else None), exit_n=len(exit_rpms),
    )


def report(a):
    if a is None:
        return "Keine auswertbaren Daten (IsRaceOn==1 fehlt)."
    lines = ["# GETRIEBE-ANALYSE (FH6)", ""]

    pp = a["peak_power_rpm"]
    if pp:
        band = f"Peak-Power ~{pp:.0f} rpm (aus Daten geschätzt)"
    else:
        band = "Peak-Power: keine Power-Daten (mit aktueller record.py neu aufnehmen)"
    lines.append(f"**Motor:** Leerlauf {a['rpm_idle']:.0f} · Max {a['rpm_max']:.0f} rpm · {band}")
    # sinnvolle Ziel-Schaltdrehzahl
    if pp:
        lines.append(f"→ Sinnvoll hochschalten knapp vor dem Begrenzer, so dass du im nächsten "
                     f"Gang wieder **nahe {pp:.0f} rpm** landest.")
    lines.append("")

    # Topspeed / Achsübersetzung
    lines.append("## Höchstgeschwindigkeit & Achse")
    lines.append(f"- Max erreicht: **{a['top_speed']:.0f} km/h** in Gang {a['top_gear']} @ {a['top_rpm']:.0f} rpm")
    frac = a["top_rpm"] / a["rpm_max"] if a["rpm_max"] else 0
    if frac >= LIMITER_FRAC:
        lines.append("  - Du drehst im höchsten Gang bis an den Begrenzer → **Achse evtl. zu kurz**, "
                     "eine längere Achsübersetzung gäbe mehr Topspeed (falls eine lange Gerade da ist).")
    elif frac < 0.85:
        lines.append(f"  - Am schnellsten Punkt nur {frac*100:.0f}% der Maxdrehzahl → entweder Strecke "
                     "zu kurvig für Topspeed, **oder** Achse zu lang (kürzer = mehr Beschleunigung).")
    else:
        lines.append(f"  - Am schnellsten Punkt bei {frac*100:.0f}% der Maxdrehzahl → grob passend.")
    lines.append("")

    # Begrenzer je Gang
    lines.append("## Begrenzer-Treffer unter Vollgas (Gänge zu kurz?)")
    if a["limiter"]:
        for g in sorted(a["limiter"]):
            lines.append(f"- Gang {g}: **{a['limiter'][g]}×** am Begrenzer")
        lines.append("  - Häufige Treffer in mittleren Gängen = diese Gänge sind kurz gespreizt "
                     "(schnell durchgeschaltet). Meist ok; nur stören, wenn du ständig anstehst.")
    else:
        lines.append("- Keine nennenswerten Begrenzer-Treffer.")
    lines.append("")

    # Hochschalt-Drehzahlabfall
    lines.append("## Drehzahlabfall beim Hochschalten (Lücken zu groß?)")
    target = a["peak_power_rpm"]
    if a["upshifts"]:
        for g in sorted(a["upshifts"]):
            pairs = a["upshifts"][g]
            rpm_before = st.mean(p[0] for p in pairs)
            rpm_after = st.mean(p[1] for p in pairs)
            note = ""
            if target and rpm_after < target - (a["rpm_max"] * 0.12):
                note = f"  ⚠️ fällt spürbar unter Peak-Power ({target:.0f}) → Lücke groß, Gang enger stellen"
            lines.append(f"- {g}→{g+1}: {rpm_before:.0f} → {rpm_after:.0f} rpm{note}")
    else:
        lines.append("- Keine Hochschaltvorgänge erkannt (zu kurze/gemächliche Fahrt?).")
    lines.append("")

    # Kurvenausgang
    lines.append("## Kurvenausgang")
    if a["exit_rpm"]:
        lines.append(f"- Drehzahl beim Vollgas-Antritt aus Kurven: **{a['exit_rpm']:.0f} rpm** "
                     f"(über {a['exit_n']} Ausgänge)")
        if target and a["exit_rpm"] < target * 0.65:
            lines.append("  - Deutlich unter Peak-Power → du beschleunigst oft in zu hohem Gang raus. "
                         "Einen Gang tiefer nehmen oder kürzere Gänge geben mehr Antritt.")
        else:
            lines.append("  - Im brauchbaren Bereich.")
    else:
        lines.append("- Keine klaren Kurvenausgänge erkannt.")
    lines.append("")
    lines.append("---")
    lines.append("*Zum Ingenieur bringen: sag dazu, ob eine LANGE Gerade auf der Strecke ist "
                 "(entscheidend für die Achsübersetzung).*")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="FH6 Getriebe-Analyse")
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
