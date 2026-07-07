# 03 · Tuning-Grundlagen — jeder Regler erklärt

Für **jeden** Tuning-Bereich in Forza: was er **physikalisch** macht, in welche Richtung du drehst,
und **welche Telemetrie** dir sagt, ob du richtig liegst. Das ist das Nachschlagewerk hinter dem
Debrief.

Zwei Grundbegriffe vorweg:

- **Untersteuern** = die Front hat weniger Grip als das Heck, das Auto „schiebt" geradeaus über
  die Vorderräder. Telemetrie: `TireSlipAngle` vorne > hinten.
- **Übersteuern** = das Heck hat weniger Grip, es „kommt", das Auto dreht ein. Telemetrie:
  `TireSlipAngle` hinten > vorne.

**Die Kernidee des Balancierens:** Machst du **eine Achse steifer** (Stabi/Feder), verliert **diese**
Achse relativ Grip. Also:
- mehr Grip vorne gewünscht (gegen Untersteuern) → **Front weicher** *oder* Heck steifer,
- mehr Grip hinten gewünscht (gegen Übersteuern) → **Heck weicher** *oder* Front steifer.

---

## 1. Reifendruck (Tire Pressure)

**Was:** Luftdruck vorne/hinten. Beeinflusst Größe und Form der Aufstandsfläche.
- **Zu hoch:** kleinere Aufstandsfläche, Reifen läuft in der Mitte heiß, weniger mechanischer Grip,
  aber direkteres Ansprechen.
- **Zu niedrig:** Reifen „walkt", Kanten laufen heiß, träge, überhitzt bei Dauerlast.

**Regeln nach:** `TireTemp` je Rad. Ziel *heiß* grob **2.0–2.2 bar (30–32 psi)**.
- Reifen zu heiß → Druck leicht **runter**.
- Reifen zu kalt → Druck leicht **rauf**.
- Balance: vorne heißer als hinten → vorderen Druck anpassen, um Temperaturen anzugleichen.

**Feintuning:** kleine Schritte (0.05 bar). Druck wirkt sofort auf Ansprechverhalten.

---

## 2. Getriebe (Gearing)

**Was:** Achsübersetzung (Final Drive) + einzelne Gangstufen.
- **Kürzer (höhere Zahl):** mehr Beschleunigung, weniger Topspeed.
- **Länger:** mehr Topspeed, trägere Beschleunigung.

**Regeln nach:** `CurrentEngineRpm`, `EngineMaxRpm`, `Speed`, `Gear`.
- Am Ende der **längsten Geraden** noch weit vom Begrenzer → länger übersetzen (Topspeed liegt brach).
- Kurz vor dem Begrenzer am Geraden-Ende → passt.
- Beim Hochschalten fällt die Drehzahl **unter das Powerband** → Gänge zu weit gespreizt, enger stellen.
- **Kurvenausgang:** Drehzahl sollte im kräftigen Drehzahlbereich landen — sonst „verhungert" der
  Antritt.

**Merke:** Getriebe kostet keine Grip-Balance, aber massiv Rundenzeit. Oft der größte einzelne Gewinn.

---

## 3. Ausrichtung — Sturz, Spur, Nachlauf (Alignment)

### Sturz (Camber)
**Was:** Neigung des Rades von oben gesehen. **Negativ** = oben nach innen. In Kurven stellt sich
das kurvenäußere Rad dadurch flacher auf die Straße → mehr Kurvengrip. Zu viel → in der Geraden
weniger Aufstandsfläche (Bremsen/Beschleunigen leidet).

**Regeln nach:** `TireSlipAngle` (Kurvengrip) + Kurven-Rundenzeit. Typisch **-1.0 bis -2.5°** vorne,
etwas weniger hinten.
> ⚠️ Ohne innen/außen-Temperaturen ist Sturz **Erfahrungssache**: in kleinen Schritten testen,
> ob Kurvengrip/Rundenzeit steigt, ohne dass Brems-/Traktionsverhalten leidet.

### Spur (Toe)
**Was:** Blickrichtung der Räder von oben.
- **Toe-out vorne** (Zehen auseinander): schärferes Einlenken, aber nervöser, mehr Reifenverschleiß.
- **Toe-in** (zusammen): mehr Geradeauslauf/Stabilität.
- **Hinten** meist minimaler Toe-in für Stabilität.

**Regeln nach:** `TireWear` (falls vorhanden) und Stabilitätsgefühl. Meist nahe **0°** halten,
nur in kleinen Dosen einsetzen.

### Nachlauf (Caster)
**Was:** Neigung der Lenkachse. **Mehr Caster** → bessere Geradeausstabilität, dynamisch mehr
Negativsturz in der Kurve, schwereres Lenkgefühl. Meist recht **hoch** (~5–7°) eingestellt.

**Regeln nach:** überwiegend Gefühl; Telemetrie nur indirekt über Stabilität/Kurvengrip.

---

## 4. Stabilisatoren (Antiroll Bars, ARB)

**Was:** verbinden linkes/rechtes Rad einer Achse; bestimmen, wie stark die Achse **wankt** — das
**wichtigste Balance-Werkzeug** ohne Grip-Nebenwirkungen auf Geraden.
- **Front steifer** → mehr Untersteuern.
- **Heck steifer** → mehr Übersteuern.

**Regeln nach:** `NormalizedSuspensionTravel` **links vs. rechts** in Kurven (Wank-Delta) +
Balance-Index (`TireSlipAngle` v/h).
- Untersteuern → vorderen Stabi **weicher** (oder hinteren steifer).
- Übersteuern → hinteren Stabi **weicher** (oder vorderen steifer).

**Merke:** Erst hiermit die Balance grob einstellen — Stabis wirken fast nur in Kurven, kaum auf
Geraden/Bremsen.

---

## 5. Federn — Steifigkeit & Höhe (Springs)

### Federrate (Stiffness)
**Was:** wie stark die Feder der Last widersteht.
- **Steifer:** schnellerer Lastwechsel, weniger Wanken/Nicken, aber weniger Schluckvermögen bei
  Bodenwellen (Rallye/Schotter → weicher!).
- **Weicher:** mehr mechanischer Grip auf unebenem Belag, aber mehr Wanken.

**Regeln nach:** `NormalizedSuspensionTravel`.
- Erreicht regelmäßig **1.0 (Anschlag)** → zu weich, **steifer** stellen.
- Nutzt kaum Federweg / Auto „schwimmt" auf Wellen → ggf. weicher.

### Höhe (Ride Height)
**Was:** Bodenabstand. **Niedriger** = tieferer Schwerpunkt = weniger Wanken, mehr Grip (und in
manchen Klassen niedrigerer PI). Zu tief → **setzt auf**.

**Regeln nach:** `NormalizedSuspensionTravel` Richtung 1.0 auf Curbs/Wellen → höher stellen.
Auf glattem Asphalt so tief wie möglich, ohne Aufsetzen.

---

## 6. Dämpfer — Zug- & Druckstufe (Damping: Rebound & Bump)

**Was:** kontrollieren die **Geschwindigkeit** der Federbewegung (die Federrate bestimmt die Kraft,
der Dämpfer das Tempo).
- **Bump (Druckstufe):** Widerstand beim **Einfedern**.
- **Rebound (Zugstufe):** Widerstand beim **Ausfedern**. Faustregel: Rebound ≈ **1.5–2×** Bump.

**Wirkung auf Balance:** steifere Dämpfer an einer Achse = schnellerer Lastaufbau dort = temporär
weniger Grip dort (ähnlich Stabis, aber nur **während** des Lastwechsels).

**Regeln nach:** `NormalizedSuspensionTravel`-Verlauf über Zeit.
- **Nachschwingen** (mehrfaches Oszillieren nach einer Welle) → Rebound zu weich, **steifer**.
- Auto wirkt „hölzern"/springt über Curbs → Dämpfer zu steif, weicher.

**Merke:** Dämpfer sind Feintuning **nach** Federn/Stabis, nicht davor.

---

## 7. Aerodynamik (Downforce)

**Was:** Anpressdruck vorne/hinten (nur bei Autos mit verstellbaren Flügeln).
- **Mehr Downforce:** mehr Grip bei **hohem** Tempo, aber mehr Luftwiderstand → weniger Topspeed.
- **Front vs. Heck** ist ein **geschwindigkeitsabhängiges** Balance-Werkzeug.

**Regeln nach:** Balance-Index getrennt für **schnelle** vs. **langsame** Kurven (`Speed` + `TireSlipAngle`).
- Untersteuern **nur schnell** → mehr Front-Downforce (oder weniger hinten).
- Übersteuern **nur schnell** → mehr Heck-Downforce.
- Kurvenreiche, langsame Strecke → Downforce runter für Topspeed, sofern Grip reicht.

---

## 8. Bremsen (Brakes)

**Was:** Bremsbalance (Front/Heck-Verteilung) + Bremsdruck.
- **Balance nach vorn:** stabileres Bremsen, aber Front blockiert früher.
- **Balance nach hinten:** schärferes Einlenken beim Bremsen, aber Heck wird nervös.
- **Druck:** höher = mehr Verzögerung, aber leichter Blockieren.

**Regeln nach:** `WheelRotationSpeed` + `TireSlipRatio` beim Bremsen.
- **Vorderräder blockieren** (Drehzahl bricht ein) → Balance nach hinten oder Druck runter.
- **Hinterräder blockieren / Heck wird instabil beim Bremsen** → Balance nach vorn.

---

## 9. Differenzial (Differential)

Das komplexeste, aber traktionsentscheidende Werkzeug. Regelt, wie Drehmoment zwischen den Rädern
einer Achse verteilt wird, wenn sie unterschiedlich schnell drehen.

- **Acceleration (Beschleunigungssperre):** wie stark die Räder **unter Gas** verblockt werden.
  - **Höher:** mehr Traktion beim Rausbeschleunigen, aber mehr **Power-On-Untersteuern** (FWD/AWD)
    bzw. bei RWD potenziell Heck-Ausbrechen, wenn zu hoch.
  - **Niedriger:** Räder drehen freier, wendiger, aber inneres Rad dreht leichter durch.
- **Deceleration (Schubsperre):** Verblockung **beim Gaswegnehmen/Bremsen** → Stabilität beim
  Einlenken. Höher = stabileres Heck beim Anbremsen, aber weniger Einlenkschärfe.
- **AWD-Balance (Center):** Drehmomentverteilung vorne/hinten. Mehr nach hinten = heckbetonteres,
  agileres Verhalten; mehr nach vorn = stabiler, mehr Untersteuern.

**Regeln nach:** `TireSlipRatio` & `WheelRotationSpeed` der **Antriebsräder** beim Rausbeschleunigen.
- Inneres Antriebsrad dreht durch (SlipRatio-Spitze, Drehzahl > Außenrad) → **Accel-Lock erhöhen**.
- Power-On-Untersteuern, Front schiebt beim Gasgeben → **Accel-Lock senken**.
- Heck nervös beim Anbremsen → **Decel-Lock erhöhen**.

---

## Reihenfolge beim Abstimmen (Empfehlung)

Nicht alles auf einmal. Grobe Wirkung zuerst, Feintuning zuletzt:

```
1. Reifendruck        → Temperaturfenster treffen
2. Getriebe           → Powerband & Topspeed passend
3. Stabilisatoren     → Grundbalance (Unter-/Übersteuern) grob einstellen
4. Federn + Höhe      → Aufsetzen vermeiden, Wanken begrenzen
5. Ausrichtung        → Sturz für Kurvengrip, Spur minimal
6. Differenzial       → Traktion am Kurvenausgang
7. Bremsen            → Blockieren & Anbrems-Balance
8. Aero               → geschwindigkeitsabhängige Restbalance
9. Dämpfer            → Feinschliff über Bodenwellen/Curbs
```

Und **immer nur eine Sache pro Testrunde** — sonst ist die Telemetrie nicht eindeutig zuzuordnen.

➡️ Weiter: [`04-debrief-workflow.md`](04-debrief-workflow.md)
