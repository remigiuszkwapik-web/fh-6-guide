# 05 · Diagnose-Playbook

Konkrete Fälle: **Symptom → Telemetrie-Signatur → Ursache → Eingriff (nach Priorität)**.
Das ist die Wissensbasis, aus der der Debrief seine Vorschläge zieht.

**Immer nur den obersten passenden Eingriff pro Runde testen**, dann nachmessen. Die Liste ist nach
Wirkungsstärke/Nebenwirkungsarmut sortiert.

Legende: `SA` = TireSlipAngle, `SR` = TireSlipRatio, `ST` = NormalizedSuspensionTravel,
`v/h` = vorne/hinten, `L/R` = links/rechts.

---

## A · Untersteuern beim **Einlenken** (Kurveneingang)

**Signatur:** `SA` vorne ≫ hinten schon beim Anlenken; Gierrate < Lenkbefehl; oft hohes Wank-Delta vorne.

**Ursache:** Front baut zu langsam/zu wenig Grip auf; Frontachse zu steif oder Geometrie zu zahm.

**Eingriffe (Reihenfolge):**
1. Vorderer **Stabilisator weicher**.
2. Etwas mehr **negativer Sturz vorne**.
3. Etwas **Toe-out vorne** (Vorsicht: nervöser).
4. Vordere **Federn weicher** (wenn Stabi allein nicht reicht).
5. **Bremsbalance leicht nach hinten** (hilft beim Trail-Braking-Einlenken).

---

## B · Untersteuern in der **Kurvenmitte** (konstant)

**Signatur:** `SA` vorne > hinten am Scheitelpunkt bei konstantem Gas; Temps vorne höher als hinten.

**Ursache:** mechanische Grip-Balance zu frontlastig belastet.

**Eingriffe:**
1. Vorderer **Stabilisator weicher** **oder** hinterer steifer.
2. **Reifendruck vorne** anpassen (Richtung Zielfenster, falls vorne zu heiß → leicht runter).
3. Mehr **negativer Sturz vorne**.
4. Bei Aero-Autos in schnellen Kurven: **Front-Downforce hoch**.

---

## C · Untersteuern beim **Rausbeschleunigen** (Power-On, v. a. FWD/AWD)

**Signatur:** Front schiebt, sobald Gas kommt; `SR` an **Vorder**rädern steigt (FWD); Gierrate fällt beim Gasgeben.

**Ursache:** Diff verblockt unter Gas zu stark → Front will geradeaus.

**Eingriffe:**
1. **Differenzial-Beschleunigungssperre senken**.
2. Bei AWD: **Center-Balance nach hinten** (mehr Heckanteil).
3. Hinteren **Stabilisator weicher** (mehr Heckrotation).

---

## D · Übersteuern beim **Einlenken / Gaswegnehmen** (Lift-off / Trail-Braking)

**Signatur:** Heck wird leicht beim Lösen des Gases oder unter Restbremse; `SA` hinten springt hoch;
Gierrate > Lenkbefehl.

**Ursache:** Heck verliert bei Lastwechsel nach vorn den Grip; Schubsperre zu offen oder Heck zu steif.

**Eingriffe:**
1. **Differenzial-Schubsperre (Decel) erhöhen**.
2. Hinterer **Stabilisator weicher** **oder** vorderer steifer.
3. **Bremsbalance leicht nach vorn**.
4. Etwas **Toe-in hinten** für Stabilität.

---

## E · Übersteuern beim **Rausbeschleunigen** (Power-On, v. a. RWD)

**Signatur:** Heck bricht beim Gasgeben aus; `SR` an **Hinter**rädern-Spitze; inneres Hinterrad
`WheelRotationSpeed` ≫ äußeres.

**Ursache:** zu wenig Traktion hinten — entweder Diff öffnet zu früh (Innenrad dreht durch) **oder**
zu viel Verblockung wirft das Heck raus. Erst unterscheiden!

**Eingriffe:**
1. Wenn **inneres Rad durchdreht** (Drehzahl-Spreizung L/R groß): **Accel-Sperre erhöhen**.
2. Wenn **beide** Hinterräder gleichmäßig durchdrehen: Heck-**Grip** erhöhen → hinterer Stabi/Feder
   **weicher**, mehr **Sturz hinten**, **Reifendruck hinten** ins Fenster.
3. Sanfter: **Accel-Sperre senken**, falls zu hoch eingestellt und Heck bei Lastaufbau ruckt.
4. Aero-Autos: **Heck-Downforce hoch** (schnelle Kurven).

---

## F · Auto **setzt auf** / wird über Curbs instabil

**Signatur:** `ST` erreicht **1.0** (Anschlag) auf Wellen/Curbs; danach plötzlicher Balance-Sprung.

**Ursache:** Höhe zu niedrig oder Federn zu weich fürs Terrain.

**Eingriffe:**
1. **Höhe** an der betroffenen Achse anheben.
2. **Federn steifer** an der Achse, die anschlägt.
3. Auf Schotter/Rallye generell: **weicher + höher** (Gegenteil von Asphalt!).

---

## G · **Bremsblockierer** / instabil beim Anbremsen

**Signatur:** `WheelRotationSpeed` eines Rades bricht beim Bremsen gegen `Speed` ein; `SR` negativ/Spitze.

**Ursache:** Bremskraft an dem Rad übersteigt den Grip; falsche Balance oder zu viel Druck.

**Eingriffe:**
1. **Vorne** blockiert → Bremsbalance nach **hinten** oder **Druck runter**.
2. **Hinten** blockiert / Heck nervös → Balance nach **vorn**.
3. Grundsätzlich zu leicht blockierend → **Bremsdruck** insgesamt senken.

---

## H · Reifen **überhitzen** über die Runde

**Signatur:** `TireTemp` steigt über die Runde immer weiter, über ~93 °C, an einer Achse stärker.

**Ursache:** Dauerüberlastung — Druck falsch, Achse arbeitet zu hart, oder Fahrstil/zu viel Schlupf.

**Eingriffe:**
1. **Reifendruck** der heißen Achse leicht anpassen (meist runter, wenn zu heiß).
2. Balance entlasten: heiße Achse **relativ entlasten** (siehe A–E je nach Grip-Balance).
3. Prüfen, ob Dauer-`SR`/`SA` zu hoch → oft Fahrstil oder zu aggressives Diff/Aero-Setup.

---

## Priorisierungs-Logik des Debriefs (Pseudocode)

So entscheidet der Analyzer später, **welchen** Fall er meldet, wenn mehrere zutreffen:

```
1. Sicherheit/Zeitfresser zuerst:
   - Aufsetzen (F) und Blockierer (G) haben Vorrang — sie kosten am meisten und
     verfälschen jede Balance-Messung.
2. Grip-Balance nach KURVENPHASE trennen:
   - Wo tritt es am stärksten auf? Eingang (A/D) / Mitte (B) / Ausgang (C/E)
   - Das bestimmt, WELCHER Regler drankommt (Stabi vs. Diff vs. Aero).
3. Schnell vs. langsam trennen:
   - nur schnell betroffen  -> zuerst Aero anfassen
   - auch/ nur langsam      -> mechanisch (Stabi/Feder/Diff)
4. Temperatur als Quer-Check:
   - heiße Achse deckt sich mit der grip-schwachen? -> bestätigt die Diagnose
5. Immer NUR den obersten Eingriff des gewählten Falls vorschlagen.
```

➡️ Begriffe: [`glossar.md`](glossar.md)
