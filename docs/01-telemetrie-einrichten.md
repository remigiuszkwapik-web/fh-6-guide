# 01 · „Data Out" auf PC/Windows einrichten

Ziel dieses Kapitels: FH6 sendet Telemetrie, und wir bestätigen, dass sie ankommt — **bevor**
wir irgendetwas analysieren. Ohne bestätigten Datenstrom ist alles andere Ratespiel.

---

## Was „Data Out" ist

Forza kann seine Telemetrie als **UDP-Stream** ins Netzwerk schicken. UDP heißt: das Spiel feuert
kleine Datenpakete an eine Ziel-IP und einen Port — „fire and forget", ohne Rückkanal. Bei jedem
Physik-Tick (~60x pro Sekunde) geht ein Paket raus mit dem kompletten aktuellen Fahrzeugzustand.

Ein Empfängerprogramm (unser Tune Helper) lauscht auf diesem Port und liest die Pakete mit.

```
   ┌───────────────┐        UDP-Pakete (~60/s)        ┌──────────────────┐
   │   FH6 (Spiel) │  ───────────────────────────►    │  Tune Helper     │
   │   "Data Out"  │     Ziel-IP : Port  z.B.          │  (UDP-Listener)  │
   └───────────────┘     127.0.0.1 : 5300              └──────────────────┘
```

---

## Einrichtung im Spiel

> Menüpfad nach FH5-Vorbild; in FH6 kann die Beschriftung leicht abweichen, die Optionen sind
> aber dieselben.

1. **Einstellungen → HUD und Gameplay** (in FH5: ganz unten der Abschnitt „Telemetrie / Data Out").
2. **Data Out: EIN**
3. **Data Out IP-Adresse:** die IP des Rechners, auf dem der Helper läuft.
   - Helper läuft auf **demselben PC** wie das Spiel → `127.0.0.1` (localhost).
   - Helper läuft auf einem **zweiten Gerät** im selben Netzwerk → dessen lokale IP,
     z. B. `192.168.1.42` (auf dem Zielgerät mit `ipconfig` herausfinden).
4. **Data Out IP-Port:** eine freie Portnummer, z. B. `5300`. Merken — der Helper muss auf
   **genau diesem** Port lauschen.
5. **Data Out Paket-Format / -Typ:** falls FH6 (wie FM) zwischen Formaten wählen lässt, nimm das
   **volle „Dash"-Format** (nicht „Sled") — nur das enthält Reifentemperaturen, Leistung, Runden usw.

---

## Windows-Firewall

Beim ersten Empfang fragt Windows evtl. nach einer Firewall-Freigabe für das Empfängerprogramm
(Python o. ä.). **Erlauben** (privates Netzwerk reicht). Ohne Freigabe kommen keine Pakete an,
wenn Spiel und Helper auf verschiedenen Geräten laufen. Auf demselben PC via `127.0.0.1` ist die
Firewall meist unkritisch.

---

## Schnelltest: Kommen überhaupt Pakete an?

Bevor wir irgendetwas parsen, nur zählen, ob **Bytes** eintreffen. Dieses Mini-Skript reicht
(Python 3, kommt im Repo später als `tools/sniff.py`):

```python
import socket

PORT = 5300  # muss zum "Data Out IP-Port" im Spiel passen

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))   # 0.0.0.0 = auf allen Netzwerk-Interfaces lauschen
print(f"Lausche auf UDP-Port {PORT} … starte im Spiel ein Rennen und fahr los.")

while True:
    data, addr = sock.recvfrom(2048)   # ein Paket empfangen
    print(f"Paket von {addr}: {len(data)} Bytes")
```

**Erwartung:** Sobald du im Spiel **fährst** (nicht im Menü!), läuft eine Flut von Zeilen durch:

```
Paket von ('127.0.0.1', 51234): 331 Bytes
Paket von ('127.0.0.1', 51234): 331 Bytes
...
```

- **Es kommen Zeilen** → Data Out funktioniert. 🎉 Weiter mit
  [`02-telemetrie-felder.md`](02-telemetrie-felder.md).
- **Es kommt nichts** → Checkliste unten.

### Die Paketgröße verrät das Format

Die Byte-Zahl pro Paket identifiziert das Format (Erfahrungswerte aus FH5/FM):

| Bytes | Format | Inhalt |
|---|---|---|
| 232 | „Sled" (V1) | nur Physik-Grunddaten, **keine** Reifentemps/Runden |
| 311 | „Dash" (FM, V2) | volles Format |
| 331 | „Dash" (FH5, V2) | volles Format inkl. Horizon-Position |

> **FH6-Verifikation:** Notiere dir die **tatsächliche** Byte-Zahl, die dein Schnelltest ausgibt.
> Weicht sie von diesen Werten ab, hat FH6 das Format angepasst — wir gleichen die Byte-Offsets
> in [`02-telemetrie-felder.md`](02-telemetrie-felder.md) dann an den echten Wert an. Genau dafür
> ist dieser Test da.

---

## Fehlersuche

| Problem | Ursache / Lösung |
|---|---|
| Keine Pakete, obwohl im Menü | Data Out sendet oft nur **während der Fahrt**. Ins Rennen, losfahren. |
| Keine Pakete, Helper auf 2. Gerät | Falsche Ziel-IP im Spiel, oder Firewall blockt. IP mit `ipconfig` prüfen, Freigabe erteilen. |
| `OSError: Address already in use` | Port doppelt belegt (Skript läuft noch, oder anderes Tool lauscht). Skript beenden / anderen Port wählen. |
| Pakete kommen, aber Größe unerwartet | Anderes Format eingestellt (Sled statt Dash) oder FH6-Änderung. Format im Spiel prüfen, Byte-Zahl notieren. |
| Werte später „unsinnig" | Häufig `IsRaceOn == 0`: außerhalb eines aktiven Rennens sind viele Felder 0/Müll. Nur Daten mit `IsRaceOn == 1` auswerten. |

---

## Wichtig fürs spätere Auswerten: `IsRaceOn`

Das allererste Feld jedes Pakets ist `IsRaceOn` (1 = Rennen läuft & Physik aktiv, 0 = Pause/Menü/
Rückspulen). **Alle** Analysen ignorieren Pakete mit `IsRaceOn == 0` — sonst verfälschen Standzeiten,
Pausen und Rückspuler die Auswertung. Das ist die wichtigste Filterregel im ganzen Tool.

➡️ Weiter: [`02-telemetrie-felder.md`](02-telemetrie-felder.md)
