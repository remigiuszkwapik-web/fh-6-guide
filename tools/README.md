# tools/ — Der Tune Helper (Phase 2)

Lokale Python-Werkzeuge, die die FH6-Telemetrie aufnehmen und zu einem
Ingenieurs-Bericht verdichten. **Keine Installation nötig** — nur Python 3
(Standard-Bibliothek, keine Pakete).

| Datei | Zweck |
|---|---|
| `forza_format.py` | Parser: rohe UDP-Bytes → benannte Felder (Byte-Offset-Tabelle) |
| `sniff.py` | Schnelltest: kommen Pakete an? Stimmt das Format? |
| `record.py` | Nimmt eine Fahrsession als CSV auf |
| `debrief.py` | Rechnet aus der CSV den Ingenieurs-Bericht (Markdown) |

## Ablauf

```
FH6 ──UDP──► record.py ──► session.csv ──► debrief.py ──► bericht.md ──► [bei Claude einfügen]
```

### 0. Voraussetzung
FH6: **Data Out = EIN**, IP `127.0.0.1`, Port `5300`, Format **Dash**
(Details: [`../docs/01-telemetrie-einrichten.md`](../docs/01-telemetrie-einrichten.md)).

### 1. Erst testen, ob Daten ankommen
```bash
python sniff.py
```
Ins Rennen, losfahren. Es sollten Zeilen mit Speed/RPM/Reifentemps erscheinen.
**Notiere die Byte-Zahl des ersten Pakets** — sie bestätigt das Format.
Kommen Warnungen (⚠️) oder unplausible Werte → FH6 hat evtl. die Offsets geändert,
dann melde mir die Byte-Zahl und wir passen `forza_format.py` an.

### 2. Session aufnehmen
```bash
python record.py --out goliath.csv --raceonly
```
2 saubere Runden fahren, dann **Strg+C**.

### 3. Debrief erzeugen
```bash
python debrief.py goliath.csv --out bericht.md
```

### 4. Mit dem Ingenieur (Claude) besprechen
Inhalt von `bericht.md` hier in den Chat einfügen und dazuschreiben, **was dich
beim Fahren am meisten stört und wo in der Kurve**. Dann bekommst du Diagnose,
Begründung und genau eine Änderung — siehe
[`../docs/06-ingenieur-bericht.md`](../docs/06-ingenieur-bericht.md).

### 5. Ändern & nachmessen
Genau die eine empfohlene Änderung im Setup vornehmen, dann Schritt 2–4 mit
**denselben Runden** wiederholen. Vorher/Nachher vergleichen.

## Hinweis zu den Zahlen

Die Schwellen in `debrief.py` (ab wann "Untersteuern", "Durchdrehen" usw.) und
die Einheit des Schräglaufwinkels sind **vorläufige Heuristiken**. Der Bericht ist
die Datengrundlage — die endgültige Deutung passiert im Dialog. Sobald echte
FH6-Daten da sind, kalibrieren wir die Schwellen nach.
