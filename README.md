# FH6 Tune Helper — Dein Renningenieur

Ein Lern- und Werkzeug-Projekt, um **Auto-Tuning in Forza Horizon 6 wirklich zu verstehen** —
statt fertige Setups aus einem Konfigurator zu kopieren, die du nicht nachvollziehen kannst.

Die Idee: Nicht *„hier ist das beste Setup"*, sondern ein **Ingenieur**, der

1. dich fragt, was das Auto tut („untersteuert es beim Einlenken, oder kommt das Heck beim Rausbeschleunigen?"),
2. dir sagt, welche **Telemetriedaten** er dazu sehen muss,
3. eine Runde mit dir „mitfährt", die Daten misst,
4. und dir **erklärt, warum** — und dann *eine* gezielte Änderung vorschlägt, die du selbst verstehst.

> **Status:** Phase 1 — Konzept & Lern-Dokumentation. Der Code (UDP-Empfänger, Parser,
> Debrief-Analyse) folgt in Phase 2. Siehe [Roadmap](#roadmap).

---

## Kann man überhaupt an die Daten kommen?

**Ja — über „Data Out".** Die Forza-Reihe (FH4, FH5, Forza Motorsport) sendet seit Jahren
einen Live-Telemetrie-Stream per UDP: ~60 Pakete pro Sekunde an eine IP/Port deiner Wahl.
FH6 setzt das mit sehr hoher Wahrscheinlichkeit fort.

Was **nicht** geht: das fertige Setup (Federrate, Sturz, Diff-Sperre) direkt aus dem Spiel
auslesen. Das braucht ein echter Ingenieur aber auch gar nicht — er liest **Wirkung**, nicht
die eingestellten Zahlen:

| Telemetrie | verrät etwas über |
|---|---|
| Reifentemperatur je Rad | Luftdruck, Sturz-Tendenz, Überlastung |
| Ein-/Ausfederung je Rad | Federn, Höhe, Stabilisatoren, Dämpfer |
| Schräglaufwinkel & Schlupf je Rad | Differenzial, Spur, Balance |
| Gier-/Nick-/Wankrate | Über-/Untersteuern **objektiv** messen |
| Radgeschwindigkeit je Rad | Bremsblockieren, Durchdrehen, Diff-Verhalten |
| Gas/Bremse/Lenkung/Gang/Drehzahl | Fahrereingaben & Getriebe |

> ⚠️ **Ehrlicher Hinweis zur Grenze:** Forza liefert **eine** Temperatur pro Reifen, nicht
> innen/mitte/außen wie echte Rennsensoren. Klassisches Sturz-Tuning über den Temperaturverlauf
> quer über die Lauffläche ist damit nicht 1:1 möglich. Wir gleichen das über Schräglaufwinkel,
> Federweg, Gesamttemperatur und dein gefühltes Verhalten aus. Details in
> [`docs/02-telemetrie-felder.md`](docs/02-telemetrie-felder.md).

---

## So lernst du mit diesem Repo

Lies die Dokumente in dieser Reihenfolge:

1. **[`docs/01-telemetrie-einrichten.md`](docs/01-telemetrie-einrichten.md)**
   „Data Out" auf PC/Windows aktivieren und testen, dass Daten ankommen.
2. **[`docs/02-telemetrie-felder.md`](docs/02-telemetrie-felder.md)**
   Was jedes Datenfeld bedeutet — und was es fürs Tuning aussagt.
3. **[`docs/03-tuning-grundlagen.md`](docs/03-tuning-grundlagen.md)**
   Jeder Tuning-Regler erklärt: was er physikalisch tut und welche Telemetrie ihn steuert.
4. **[`docs/04-debrief-workflow.md`](docs/04-debrief-workflow.md)**
   Der Ingenieur-Prozess: Symptom → Telemetrie → Diagnose → *eine* Änderung → nachmessen.
5. **[`docs/05-diagnose-playbook.md`](docs/05-diagnose-playbook.md)**
   Konkrete Fälle mit ihrer „Telemetrie-Signatur" und dem passenden Eingriff.
6. **[`docs/glossar.md`](docs/glossar.md)** — Begriffe zum Nachschlagen.

---

## Der Debrief-Loop (das Kernprinzip)

```
   ┌─────────────────────────────────────────────────────────┐
   │  1. SYMPTOM        Was fühlst du? Wo im Kurvenverlauf?    │
   │  2. MESSEN         2 saubere Runden, Data Out läuft mit.  │
   │  3. DIAGNOSE       Telemetrie-Signatur → echte Ursache.   │
   │  4. EINE ÄNDERUNG  Nur ein Regler, gerichtet & klein.     │
   │  5. NACHMESSEN     Gleiche Runden, Vorher/Nachher.        │
   └───────────────┬─────────────────────────────────────────┘
                   └──────────► zurück zu 1 (nächstes Symptom)
```

**Goldene Regel:** immer nur **eine** Sache pro Runde ändern. Sonst weißt du nie, *welche*
Änderung geholfen (oder geschadet) hat — genau der Fehler, den Konfiguratoren dir nicht abtrainieren.

---

## Roadmap

- [x] **Phase 1 — Konzept & Doku** (dieses Repo, aktuell)
- [ ] **Phase 2 — Telemetrie-Empfänger:** Python-UDP-Listener + Parser für das FH6-„Dash"-Format,
      der die Rohpakete in lesbare Werte übersetzt und eine Runde aufzeichnet (CSV).
- [ ] **Phase 3 — Debrief-Analyse:** Aus der Aufzeichnung automatisch Balance, Reifentemps,
      Federweg-Auslastung, Bremsblockierer usw. berechnen und als Ingenieurs-Report ausgeben.
- [ ] **Phase 4 — Dialog-Ingenieur:** Symptom-Abfrage → gezielte Auswertung → Änderungsvorschlag
      mit Begründung.

---

## Wichtig zur Genauigkeit

Das dokumentierte Telemetrie-Format basiert auf dem öffentlich bekannten **FH5 / Forza Motorsport
„Data Out"-Format**. FH6 kann das Format minimal geändert haben (z. B. neue Felder am Ende).
Sobald echte FH6-Pakete vorliegen, verifizieren wir Byte-Offsets und passen den Parser an —
siehe die Prüf-Anleitung in [`docs/01-telemetrie-einrichten.md`](docs/01-telemetrie-einrichten.md).
