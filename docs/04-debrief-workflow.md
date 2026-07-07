# 04 · Der Debrief-Workflow

So arbeitet der Ingenieur **mit dir** — genau die Arbeitsweise, die du wolltest: eine Runde fahren,
danach gemeinsam auswerten. Kein Konfigurator-„hier ist das Beste", sondern ein wiederholbarer Loop,
der dich das Abstimmen *lehrt*.

---

## Der Loop

```
   1. SYMPTOM ──► 2. MESSEN ──► 3. DIAGNOSE ──► 4. EINE ÄNDERUNG ──► 5. NACHMESSEN
        ▲                                                                    │
        └────────────────────────  nächstes Symptom  ◄──────────────────────┘
```

### 1. Symptom — was fühlst du?

Der Ingenieur fragt gezielt, **wo im Kurvenverlauf** das Problem auftritt. Das ist entscheidend,
weil dieselbe „Untersteuern"-Beschwerde je nach Phase eine völlig andere Ursache hat:

- **Kurveneingang / Einlenken** (Bremse, erstes Einlenken)
- **Kurvenmitte** (konstant, Scheitelpunkt)
- **Kurvenausgang** (Gas geben, Rausbeschleunigen)
- **schnell vs. langsam** (aero- vs. mechanisch dominiert)

Beispiel-Dialog:
> **Ing.:** „Untersteuert es beim *Einlenken* oder erst in der *Mitte*? Und eher in schnellen
> oder langsamen Kurven?"
> **Du:** „Beim Einlenken, vor allem in langsamen Haarnadeln."
> **Ing.:** „Klingt nach mechanischem Einlenk-Untersteuern. Ich schau mir Front-Schräglaufwinkel
> und Wank-Delta vorne an. Fahr mir zwei saubere Runden."

### 2. Messen — 2 saubere Runden

- **Data Out läuft mit** (siehe [`01`](01-telemetrie-einrichten.md)).
- **Gleiche Strecke, gleiche Bedingungen** wie beim nächsten Test — sonst ist Vorher/Nachher wertlos.
- **Sauber fahren:** keine Ausritte, kein Rückspulen. Der Analyzer filtert `IsRaceOn == 0` raus,
  aber grobe Fahrfehler verfälschen trotzdem.
- 2 Runden reichen, damit Ausreißer sich rausmitteln.

### 3. Diagnose — Telemetrie-Signatur

Der Analyzer rechnet aus der Aufzeichnung die **Kennzahlen** aus ([`02`](02-telemetrie-felder.md))
und ordnet sie einer **Signatur** aus dem [Playbook](05-diagnose-playbook.md) zu. Wichtig: Er
bestätigt (oder widerlegt!) dein Bauchgefühl mit Zahlen.

> **Ing.:** „Bestätigt: Front-Schräglaufwinkel in den Haarnadeln im Schnitt 6.2°, hinten 3.8° —
> die Front ist klar überfordert. Federweg links/rechts vorne läuft weit auseinander, viel Wanken.
> Das ist mechanisch, nicht aero."

### 4. Eine Änderung — gerichtet & klein

- **Genau ein Regler.** Der Ingenieur nennt Regler, Richtung, kleine Dosis — **und die Begründung**.
- Klein, damit du die Wirkung sauber siehst und nicht überschießt.

> **Ing.:** „Vorderen Stabilisator eine Stufe **weicher**. Das gibt der Front in langsamen Kurven
> mehr Grip, ohne den Topspeed anzufassen. Warum Stabi und nicht Feder? Weil das Problem fast nur
> in Kurven auftritt — Stabis wirken genau da, Federn würden auch das Bremsen verändern."

### 5. Nachmessen — Vorher/Nachher

- **Exakt dieselben Runden** noch mal, Data Out läuft.
- Der Analyzer stellt **Vorher/Nachher** gegenüber: Balance-Index, Kurven-Rundenzeit, Temps.
- **Besser** → behalten, nächstes Symptom. **Schlechter/gleich** → zurückdrehen, andere Hypothese.

> **Ing.:** „Front-Schräglauf jetzt 5.1° (−1.1°), Haarnadel 0.15 s schneller, keine neue
> Übersteuer-Tendenz am Ausgang. Behalten. Was stört dich als Nächstes?"

---

## Warum das dich das Tuning *lehrt*

Konfiguratoren nehmen dir den mittleren Teil weg — du siehst nur Eingabe → fertiges Setup. Dieser
Loop macht jeden Schritt **explizit und begründet**:

- Du lernst, **Symptome präzise zu beschreiben** (Phase der Kurve, schnell/langsam).
- Du siehst, welche **Telemetrie** ein Symptom bestätigt.
- Du verknüpfst **Regler → Wirkung** über echte Vorher/Nachher-Zahlen.
- Nach ein paar Sessions diagnostizierst du selbst — das Tool wird zum Sparringspartner, nicht zur Krücke.

---

## Disziplinregeln (die der Ingenieur durchsetzt)

1. **Eine Änderung pro Runde.** Sonst ist die Ursache nicht zuzuordnen.
2. **Gleiche Strecke/Bedingungen** für Vorher/Nachher.
3. **Erst grob, dann fein** — Reihenfolge aus [`03`](03-tuning-grundlagen.md) (Druck → Getriebe →
   Stabis → …), nicht mit Dämpfer-Feintuning anfangen.
4. **Zahlen schlagen Bauchgefühl bei Konflikt** — aber das Bauchgefühl liefert die *Frage*, die
   Telemetrie die *Antwort*.
5. **Bei Verschlechterung sofort zurück.** Kein „vielleicht wird's mit der nächsten Änderung besser".

---

## Was der Analyzer pro Debrief ausgibt (Phase-3-Ziel)

Ein Report etwa so:

```
── DEBRIEF · Strecke X · Auto Y · 2 Runden ──────────────────────
Balance-Index (SlipAngle v−h):   +2.4°   → UNTERSTEUERN (mittel)
  · langsame Kurven:             +3.1°   → stark
  · schnelle Kurven:             +0.6°   → neutral
Reifentemps (°C)  FL 88  FR 91  RL 79  RR 80   → Front heiß, Heck kühl
Federweg-Auslastung:  vorne 12% am Anschlag (Curbs), hinten 3%
Wank-Delta vorne:     hoch   · hinten: mittel
Traktions-Events:     4× Innenrad-Schlupf am Ausgang (RWD)
Blockier-Events:      1× vorne links (Anbremsen T3)
─────────────────────────────────────────────────────────────────
VORSCHLAG (1 Änderung):
  Vorderer Stabilisator −1 Stufe.
  Grund: Untersteuern konzentriert in langsamen Kurven + hohes
  Wank-Delta vorne. Stabi wirkt gezielt in Kurven, ohne Topspeed
  oder Bremsen zu verändern. Danach dieselben 2 Runden zum Vergleich.
```

➡️ Konkrete Fälle: [`05-diagnose-playbook.md`](05-diagnose-playbook.md)
