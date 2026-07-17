"""
debrief.py — Wertet eine aufgezeichnete Session (CSV von record.py) aus und
schreibt einen Ingenieurs-Bericht (Markdown), den du beim Ingenieur (Claude)
einfügst.

Aufruf:
    python debrief.py session.csv
    python debrief.py session.csv --out bericht.md

Was es rechnet (siehe docs/02 + docs/05):
    · Balance-Index (Schräglauf vorne − hinten), getrennt langsam/schnell
    · Reifentemperaturen je Rad
    · Federweg-Auslastung (Aufsetzen) je Achse
    · Wank-Delta (links/rechts) je Achse
    · Traktions-Events (Antriebsrad-Schlupf beim Gasgeben)
    · Blockier-Events (Rad blockiert beim Bremsen)
und leitet daraus EINEN priorisierten Änderungsvorschlag ab.

Wichtig: Die Schwellen und die Schräglauf-Einheit sind vorläufige Heuristiken.
Der Bericht ist die DATENGRUNDLAGE fürs Gespräch — die finale Diagnose/Erklärung
macht der Ingenieur im Dialog mit dir.
"""

import argparse
import csv
import json
import os
import statistics as st

import forza_format as ff

_CARS_DB = os.path.join(os.path.dirname(__file__), "cars.json")


def car_label(ordinal):
    """Name (falls in cars.json hinterlegt) + ID; sonst nur ID/unbekannt."""
    if ordinal is None:
        return "unbekannt (alte Aufnahme ohne CarOrdinal)"
    name = None
    if os.path.exists(_CARS_DB):
        try:
            with open(_CARS_DB, encoding="utf-8") as fh:
                name = json.load(fh).get(str(ordinal))
        except (OSError, ValueError):
            pass
    return f"{name} (ID {ordinal})" if name else f"ID {ordinal} (Name mit carinfo.py setzen)"

WHEELS = ("FL", "FR", "RL", "RR")

# ── Schwellen (vorläufig, im Dialog verfeinerbar) ────────────────────────────
LAT_G_CORNER = 3.5      # m/s² seitlich → gilt als "in der Kurve"
SPEED_SLOW_FAST = 30.0  # m/s (~108 km/h): Grenze langsam/schnell
BOTTOM_THRESH = 0.97    # NormSuspTravel ab hier = quasi Anschlag
BAL_DEADZONE = 0.08     # |Balance| darunter = neutral   (roh)
BAL_STRONG = 0.30       # |Balance| darüber  = stark
SPIN_SLIP = 0.20        # SlipRatio darüber = Antriebsrad dreht durch
SPIN_ACCEL = 200        # Gas (0..255) darüber = "unter Last"
LOCK_SLIP = -0.15       # SlipRatio darunter = Rad blockiert
LOCK_BRAKE = 120        # Bremse (0..255) darüber = "am Bremsen"
MIN_SPEED = 8.0         # m/s: unter Schritttempo nicht bewerten


def fnum(row, key, default=0.0):
    """Sichere Float-Konvertierung eines CSV-Feldes."""
    v = row.get(key, "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def axle_avg(vals):
    return st.mean(vals) if vals else 0.0


def count_rising_edges(flags):
    """Zählt 0→1-Wechsel in einer Bool-Sequenz (ein Event = ein Wechsel)."""
    edges, prev = 0, False
    for f in flags:
        if f and not prev:
            edges += 1
        prev = f
    return edges


def analyze(rows):
    # Nur aktives Rennen auswerten
    rows = [r for r in rows if int(fnum(r, "IsRaceOn")) == 1]
    if not rows:
        return None

    drivetrain = int(fnum(rows[0], "DrivetrainType"))
    driven = ff.driven_wheels(drivetrain)

    # Kurven-Samples (nach seitlicher G-Kraft)
    corner = [r for r in rows if abs(fnum(r, "AccelerationX")) > LAT_G_CORNER]
    slow = [r for r in corner if fnum(r, "Speed") < SPEED_SLOW_FAST]
    fast = [r for r in corner if fnum(r, "Speed") >= SPEED_SLOW_FAST]

    def balance(sample):
        """Schräglauf vorne − hinten (Betrag). >0 = Untersteuern."""
        if not sample:
            return None
        front, rear = [], []
        for r in sample:
            front.append((abs(fnum(r, "TireSlipAngleFL")) + abs(fnum(r, "TireSlipAngleFR"))) / 2)
            rear.append((abs(fnum(r, "TireSlipAngleRL")) + abs(fnum(r, "TireSlipAngleRR"))) / 2)
        return st.mean(front) - st.mean(rear)

    bal_all, bal_slow, bal_fast = balance(corner), balance(slow), balance(fast)

    # Reifentemperaturen (°C) je Rad, Mittel über die Session
    temps = {}
    for w in WHEELS:
        vals = [ff.f_to_c(fnum(r, f"TireTemp{w}")) for r in rows if r.get(f"TireTemp{w}")]
        temps[w] = st.mean(vals) if vals else None

    # Federweg-Auslastung: Anteil Samples nahe Anschlag, je Achse
    def bottom_pct(wheels):
        hits = sum(1 for r in rows
                   if max(fnum(r, f"NormSuspTravel{w}") for w in wheels) >= BOTTOM_THRESH)
        return 100.0 * hits / len(rows)

    bottom_front = bottom_pct(("FL", "FR"))
    bottom_rear = bottom_pct(("RL", "RR"))

    # Wank-Delta (|links − rechts|) je Achse, nur in Kurven
    def roll_delta(left, right):
        if not corner:
            return 0.0
        return st.mean(abs(fnum(r, f"NormSuspTravel{left}") - fnum(r, f"NormSuspTravel{right}"))
                       for r in corner)

    roll_front = roll_delta("FL", "FR")
    roll_rear = roll_delta("RL", "RR")

    # Traktions-Events: Antriebsrad dreht unter Gas durch
    spin_flags = []
    for r in rows:
        spinning = (fnum(r, "Accel") > SPIN_ACCEL and
                    any(fnum(r, f"TireSlipRatio{w}") > SPIN_SLIP for w in driven))
        spin_flags.append(spinning)
    spin_events = count_rising_edges(spin_flags)

    # Diff-Diagnose: Beim KURVEN-Durchdrehen — dreht das kurveninnere oder -äußere
    # Antriebsrad stärker durch? Inneres Rad = offenes/zu wenig gesperrtes Diff
    # (Lock erhöhen); beide/äußeres = eher Grip-/Fahrstilthema.
    # Steer > 0 = rechts → inneres Rad rechts (…R); Steer < 0 → inneres links (…L).
    inner_spin = outer_spin = 0
    rear = ("RL", "RR") if drivetrain != 0 else ("FL", "FR")  # RWD/AWD: Heck; FWD: Front
    for r in rows:
        if fnum(r, "Accel") <= SPIN_ACCEL:
            continue
        steer = fnum(r, "Steer")
        if abs(steer) < 5:
            continue  # nur echte Kurvenlage
        sl = fnum(r, f"TireSlipRatio{rear[0]}")   # links
        sr = fnum(r, f"TireSlipRatio{rear[1]}")   # rechts
        if max(sl, sr) < SPIN_SLIP:
            continue
        inner, outer = (sr, sl) if steer > 0 else (sl, sr)
        if inner > outer:
            inner_spin += 1
        else:
            outer_spin += 1

    # Blockier-Events je Rad: SlipRatio stark negativ beim Bremsen
    lock_events = {}
    for w in WHEELS:
        flags = [(fnum(r, "Brake") > LOCK_BRAKE and fnum(r, "Speed") > MIN_SPEED and
                  fnum(r, f"TireSlipRatio{w}") < LOCK_SLIP) for r in rows]
        lock_events[w] = count_rising_edges(flags)

    # Session-Dauer (für faire "pro Minute"-Normierung verschieden langer Fahrten)
    ts = [fnum(r, "TimestampMS") for r in rows if r.get("TimestampMS")]
    duration_s = (max(ts) - min(ts)) / 1000.0 if len(ts) >= 2 else 0.0
    if duration_s <= 0:
        duration_s = len(rows) / 60.0  # Fallback: ~60 Hz annehmen

    # Rundenzeiten aus LapNumber-Wechseln (grob)
    laps = []
    last_num, last_time = None, None
    for r in rows:
        num = int(fnum(r, "LapNumber"))
        t = fnum(r, "CurrentRaceTime")
        if last_num is None:
            last_num, last_time = num, t
        elif num != last_num:
            laps.append(t - last_time)
            last_num, last_time = num, t

    return dict(
        n=len(rows), drivetrain=ff.DRIVETRAIN_NAMES.get(drivetrain, "?"),
        pi=int(fnum(rows[0], "CarPerformanceIndex")),
        bal_all=bal_all, bal_slow=bal_slow, bal_fast=bal_fast,
        temps=temps, bottom_front=bottom_front, bottom_rear=bottom_rear,
        roll_front=roll_front, roll_rear=roll_rear,
        spin_events=spin_events, lock_events=lock_events, laps=laps,
        duration_s=duration_s, inner_spin=inner_spin, outer_spin=outer_spin,
        car_ordinal=(int(fnum(rows[0], "CarOrdinal")) if rows[0].get("CarOrdinal") else None),
    )


def _bal_word(b):
    if b is None:
        return "—"
    if abs(b) < BAL_DEADZONE:
        return "neutral"
    strength = "stark" if abs(b) >= BAL_STRONG else "mittel"
    return f"{'UNTERSTEUERN' if b > 0 else 'ÜBERSTEUERN'} ({strength})"


def suggest(a):
    """EIN priorisierter Vorschlag nach der Playbook-Logik (docs/05)."""
    # 1) Aufsetzen hat Vorrang (verfälscht alles andere)
    if a["bottom_front"] > 5 or a["bottom_rear"] > 5:
        axle = "vorne" if a["bottom_front"] >= a["bottom_rear"] else "hinten"
        return (f"Höhe {axle} anheben (oder Federn {axle} steifer).",
                f"Die Achse {axle} schlägt in {max(a['bottom_front'], a['bottom_rear']):.0f}% "
                f"der Zeit an den Federweg-Anschlag — das kostet Grip und verfälscht die Balance. "
                f"Erst das beheben, dann die Balance feinjustieren.")

    # 2) Blockierer beheben
    total_locks = sum(a["lock_events"].values())
    if total_locks >= 3:
        front_locks = a["lock_events"]["FL"] + a["lock_events"]["FR"]
        rear_locks = a["lock_events"]["RL"] + a["lock_events"]["RR"]
        if front_locks >= rear_locks:
            return ("Bremsbalance leicht nach hinten (oder Bremsdruck senken).",
                    f"{front_locks}× Vorderrad-Blockierer beim Anbremsen — die Front überbremst.")
        return ("Bremsbalance leicht nach vorn.",
                f"{rear_locks}× Hinterrad-Blockierer — das Heck wird beim Bremsen instabil.")

    # 3) Traktion am Ausgang
    if a["spin_events"] >= 4 and a["drivetrain"] in ("RWD", "AWD"):
        return ("Differenzial-Beschleunigungssperre erhöhen (kleiner Schritt).",
                f"{a['spin_events']}× Antriebsrad-Durchdrehen beim Gasgeben — dir fehlt Traktion "
                f"am Kurvenausgang. Wenn danach das Heck nervös wird, war es zu viel.")

    # 4) Grip-Balance — nach schnell/langsam getrennt (bestimmt Regler)
    b = a["bal_all"]
    if b is None or abs(b) < BAL_DEADZONE:
        return ("Kein klares Balance-Problem in den Daten.",
                "Die Front/Heck-Balance ist neutral. Beschreib mir, was dich beim Fahren am "
                "meisten stört — dann schauen wir gezielt in die passenden Kennzahlen.")

    worse_fast = (a["bal_fast"] is not None and a["bal_slow"] is not None
                  and abs(a["bal_fast"]) > abs(a["bal_slow"]) + BAL_DEADZONE)
    if b > 0:  # Untersteuern
        if worse_fast:
            return ("Front-Downforce erhöhen (oder Heck-Downforce senken).",
                    "Untersteuern tritt vor allem in SCHNELLEN Kurven auf → aerodynamisch. "
                    "Mehr Front-Anpressdruck gibt der Front bei Tempo Grip.")
        return ("Vorderen Stabilisator eine Stufe weicher.",
                "Untersteuern vor allem in langsamen/mittleren Kurven → mechanisch. Ein weicherer "
                "Front-Stabi gibt der Front mehr Grip, ohne Topspeed oder Bremsen anzufassen.")
    else:      # Übersteuern
        if worse_fast:
            return ("Heck-Downforce erhöhen.",
                    "Übersteuern vor allem in SCHNELLEN Kurven → aerodynamisch. Mehr Heck-Anpressdruck "
                    "stabilisiert das Heck bei Tempo.")
        return ("Hinteren Stabilisator eine Stufe weicher (oder Schubsperre erhöhen).",
                "Übersteuern vor allem in langsamen/mittleren Kurven → mechanisch. Ein weicherer "
                "Heck-Stabi gibt dem Heck mehr Grip.")


def format_report(a):
    if a is None:
        return "Keine auswertbaren Daten (keine Zeilen mit IsRaceOn==1)."
    t = a["temps"]

    def temp(w):
        return f"{t[w]:.0f}" if t[w] is not None else "—"

    action, reason = suggest(a)
    laptxt = ("  ".join(f"{l:.2f}s" for l in a["laps"]) if a["laps"] else "—")

    dur = a["duration_s"]
    per_min = (60.0 / dur) if dur > 0 else 0.0          # Faktor: Events × per_min = Events/Minute
    spin_pm = a["spin_events"] * per_min
    lock_total = sum(a["lock_events"].values())
    lock_front = a["lock_events"]["FL"] + a["lock_events"]["FR"]
    lock_pm = lock_total * per_min

    # Diff-Diagnose in Klartext
    ins, outs = a["inner_spin"], a["outer_spin"]
    tot = ins + outs
    if tot < 8:
        diff_line = "- Diff-Diagnose: zu wenig Kurven-Durchdrehen für ein Urteil."
    elif ins >= 2 * outs:
        diff_line = (f"- **Diff-Diagnose: kurveninneres Rad {ins} : {outs} äußeres** → Diff zu OFFEN "
                     "unter Gas. **Beschleunigungssperre erhöhen** bringt Traktion zum belasteten Außenrad.")
    elif outs >= 2 * ins:
        diff_line = (f"- Diff-Diagnose: äußeres Rad {outs} : {ins} inneres → eher Grip-/Fahrstilthema, "
                     "nicht mehr Sperre.")
    else:
        diff_line = (f"- Diff-Diagnose: inneres {ins} ~ äußeres {outs} → ausgewogen; Durchdrehen ist "
                     "eher reine Leistung/Grip, nicht die Sperre.")

    return f"""# DEBRIEF-BERICHT (FH6)

**Auto:** {car_label(a['car_ordinal'])} · {a['drivetrain']} · PI {a['pi']} · {a['n']} Samples · {dur:.0f}s · Runden: {laptxt}

## Balance (Schräglauf vorne − hinten, roh; + = Untersteuern)
- gesamt:   `{a['bal_all']:+.3f}`  → **{_bal_word(a['bal_all'])}**
- langsam:  `{_fmt(a['bal_slow'])}`  → {_bal_word(a['bal_slow'])}
- schnell:  `{_fmt(a['bal_fast'])}`  → {_bal_word(a['bal_fast'])}

## Reifentemperatur (°C, Mittel)
| FL | FR | RL | RR |
|----|----|----|----|
| {temp('FL')} | {temp('FR')} | {temp('RL')} | {temp('RR')} |

## Fahrwerk & Traktion
- Federweg am Anschlag:  vorne **{a['bottom_front']:.0f}%** · hinten **{a['bottom_rear']:.0f}%**
- Wank-Delta (L/R):      vorne `{a['roll_front']:.3f}` · hinten `{a['roll_rear']:.3f}`
- Traktions-Events (Durchdrehen am Gas): **{a['spin_events']}**  (**{spin_pm:.0f}/min**)
{diff_line}
- Blockier-Events:  FL {a['lock_events']['FL']} · FR {a['lock_events']['FR']} · RL {a['lock_events']['RL']} · RR {a['lock_events']['RR']}  (gesamt **{lock_pm:.0f}/min**, davon Front {lock_front})
  - _Hinweis: Bei aktivem ABS sind das meist ABS-Regeleingriffe, KEIN echtes Blockieren — dann ignorieren._

## Automatischer Erst-Vorschlag (1 Änderung)
**→ {action}**
{reason}

---
*Hinweis an den Ingenieur: Bitte die Diagnose anhand obiger Zahlen bestätigen/verfeinern,
das Warum erklären und genau EINE Änderung empfehlen. Danach dieselben 2 Runden zum Vergleich.*
"""


def _fmt(x):
    return f"{x:+.3f}" if x is not None else "—"


def main():
    ap = argparse.ArgumentParser(description="FH6 Debrief-Analyse")
    ap.add_argument("csv", help="Aufgezeichnete Session (von record.py)")
    ap.add_argument("--out", help="Bericht als Datei speichern (sonst nur Konsole)")
    args = ap.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    report = format_report(analyze(rows))
    print(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"\n(Bericht gespeichert: {args.out} — Inhalt beim Ingenieur einfügen.)")


if __name__ == "__main__":
    main()
