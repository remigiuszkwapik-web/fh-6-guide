# 02 · Die Telemetriefelder — und was sie fürs Tuning bedeuten

Hier steht, **was in einem Paket drin ist**, in welcher Reihenfolge, und — das Wichtigste —
**was ein Ingenieur daraus liest**. Das ist die Übersetzung von Rohdaten in Tuning-Entscheidungen.

> Die Reihenfolge und Typen entsprechen dem bekannten **FH5/FM „Dash"-Format**. Alles ist
> **little-endian**. FH6 kann Felder ergänzt haben; die Offsets prüfen wir mit echten Paketen
> (siehe [`01`](01-telemetrie-einrichten.md)). Die *Bedeutung* der Felder ist stabil.

Radreihenfolge in Forza ist **immer**: `FrontLeft, FrontRight, RearLeft, RearRight`
(vorne-links, vorne-rechts, hinten-links, hinten-rechts) → im Code oft `FL, FR, RL, RR`.

---

## Paketaufbau (Dash-Format)

Die Feldtypen: `s32`/`u32` = 4-Byte-Ganzzahl, `f32` = 4-Byte-Gleitkomma, `u16` = 2 Byte,
`u8`/`s8` = 1 Byte.

### Teil A — „Sled" (Physik-Grunddaten)

| Feld | Typ | Bedeutung |
|---|---|---|
| `IsRaceOn` | s32 | 1 = Rennen aktiv. **Filter: nur ==1 auswerten.** |
| `TimestampMS` | u32 | Zeitstempel (ms), für Δt zwischen Paketen |
| `EngineMaxRpm` | f32 | max. Drehzahl → Getriebe/Schaltpunkte |
| `EngineIdleRpm` | f32 | Leerlaufdrehzahl |
| `CurrentEngineRpm` | f32 | aktuelle Drehzahl → Powerband, Schaltpunkte |
| `Acceleration X/Y/Z` | f32 | Beschleunigung im Fahrzeug-Koordinatensystem (G-Kräfte) |
| `Velocity X/Y/Z` | f32 | Geschwindigkeitsvektor |
| `AngularVelocity X/Y/Z` | f32 | Drehraten. **Y = Gierrate** → Über-/Untersteuern |
| `Yaw / Pitch / Roll` | f32 | Fahrzeuglage (Gieren/Nicken/Wanken) |
| `NormalizedSuspensionTravel FL/FR/RL/RR` | f32 | Federweg **normiert 0…1** (0 = voll ausgefedert, 1 = voll eingefedert/Anschlag) |
| `TireSlipRatio FL/FR/RL/RR` | f32 | **Längs**schlupf (Antrieb/Bremse). 0 = perfekt abrollend, >0 durchdrehend/blockierend |
| `WheelRotationSpeed FL/FR/RL/RR` | f32 | Raddrehzahl (rad/s) → Blockieren/Durchdrehen erkennen |
| `WheelOnRumbleStrip FL/FR/RL/RR` | f32 | Rad auf Curb/Randstein |
| `WheelInPuddleDepth FL/FR/RL/RR` | f32 | Wassertiefe am Rad |
| `SurfaceRumble FL/FR/RL/RR` | f32 | Untergrund-Vibration (Force Feedback) |
| `TireSlipAngle FL/FR/RL/RR` | f32 | **Schräglaufwinkel** (Quer-Schlupf) → Kurvengrip & Balance |
| `TireCombinedSlip FL/FR/RL/RR` | f32 | Gesamtschlupf (längs+quer). >1 ≈ jenseits des Grip-Limits |
| `SuspensionTravelMeters FL/FR/RL/RR` | f32 | Federweg in Metern (absolut) |
| `CarOrdinal` | s32 | Fahrzeug-ID |
| `CarClass` | s32 | Klasse (D…X) |
| `CarPerformanceIndex` | s32 | PI-Wert |
| `DrivetrainType` | s32 | 0 = FWD, 1 = RWD, 2 = AWD |
| `NumCylinders` | s32 | Zylinderzahl |

### Teil B — „Dash"-Zusatz

| Feld | Typ | Bedeutung |
|---|---|---|
| `PositionX / Y / Z` | f32 | Weltposition (Horizon) → Streckenkarte, Sektoren |
| `Speed` | f32 | Geschwindigkeit (m/s) |
| `Power` | f32 | Leistung (W) |
| `Torque` | f32 | Drehmoment (Nm) |
| `TireTemp FL/FR/RL/RR` | f32 | **Reifentemperatur** (°F) → Luftdruck, Überlastung, Balance |
| `Boost` | f32 | Ladedruck |
| `Fuel` | f32 | Tankfüllung (0…1) |
| `DistanceTraveled` | f32 | zurückgelegte Strecke |
| `BestLap / LastLap / CurrentLap` | f32 | Rundenzeiten (s) |
| `CurrentRaceTime` | f32 | Rennzeit (s) |
| `LapNumber` | u16 | Rundennummer |
| `RacePosition` | u8 | Position im Feld |
| `Accel` | u8 | **Gas** 0…255 |
| `Brake` | u8 | **Bremse** 0…255 |
| `Clutch` | u8 | Kupplung 0…255 |
| `HandBrake` | u8 | Handbremse 0…255 |
| `Gear` | u8 | aktueller Gang |
| `Steer` | s8 | **Lenkeinschlag** -127…127 |
| `NormalizedDrivingLine` | s8 | Ideallinien-Abweichung |
| `NormalizedAIBrakeDifference` | s8 | KI-Bremsvergleich |

> Einige FH5-Updates hängten am Ende noch `TireWear FL/FR/RL/RR` (f32) und `TrackOrdinal` (s32) an.
> Ob FH6 diese führt, klären die echten Pakete.

---

## Von Rohdaten zu Tuning-Aussagen

Das ist der Kern. Jede Zeile: **welches Feld → welche Frage beantwortet es**.

### Balance objektiv messen (Über-/Untersteuern)
- **`TireSlipAngle` vorne vs. hinten:** Ist der Schräglaufwinkel **vorne** deutlich größer als
  hinten, „schiebt" die Front → **Untersteuern**. Ist er **hinten** größer → **Übersteuern**.
  Das ist die objektive Version deines Bauchgefühls.
- **`AngularVelocity.Y` (Gierrate) vs. `Steer`:** Dreht das Auto stärker ein, als der Lenkwinkel
  „bestellt" → Übersteuer-Tendenz. Weniger → Untersteuern.

### Reifentemperatur → Luftdruck & Last
- Zielfenster für Renn-/Sportreifen in Forza grob **~77–93 °C (170–200 °F)**. Zu kalt → zu wenig
  Grip, zu heiß → Überlastung/Abbau.
- **Achse zu heiß** relativ zur anderen → diese Achse arbeitet zu hart (oft zu weich abgestimmt
  oder falscher Druck).
- **Luftdruck:** in Forza gilt grob ein *heißer* Zieldruck von ~**2.0–2.2 bar (≈30–32 psi)**.
  Läuft der Reifen zu heiß, Druck leicht runter; zu kalt, leicht rauf.

> ⚠️ **Grenze:** Nur **eine** Temperatur pro Reifen — kein innen/mitte/außen-Verlauf. Klassisches
> Sturz-Tuning über den Quer-Temperaturverlauf ist damit **nicht** möglich. Sturz stimmen wir
> stattdessen über `TireSlipAngle`, Kurven-Rundenzeit und Grip-Gefühl ab. Nicht so „sauber" wie
> echte Rennsensoren, aber praktikabel.

### Federweg → Federn, Höhe, Stabis, Dämpfer
- **`NormalizedSuspensionTravel` erreicht 1.0** (Anschlag) → Auto **setzt auf**: Federn zu weich
  oder Höhe zu niedrig. Erreicht es 0.0 → Rad hebt ab/federt voll aus.
- **Links/rechts-Differenz** an einer Achse in der Kurve = **Wankbewegung**. Große Differenz →
  viel Rollen; über Stabilisatoren (ARB) an dieser Achse steuerbar.
- **Nachschwingen** (Wert oszilliert nach einer Bodenwelle mehrfach nach) → Dämpfer zu weich.

### Schlupf → Differenzial, Bremsen, Traktion
- **`TireSlipRatio` an einem angetriebenen Rad springt hoch beim Gasgeben** → Rad dreht durch:
  bei RWD/AWD oft **Diff-Beschleunigungssperre zu niedrig** oder Heck zu weich.
- **Innenrad dreht schneller als Außenrad** (`WheelRotationSpeed`-Vergleich links/rechts der
  Antriebsachse) beim Rausbeschleunigen → offene Sperrwirkung, mehr Accel-Lock hilft.
- **`SlipRatio` negativ / Raddrehzahl bricht gegen Speed ein beim Bremsen** → **Blockierer**:
  Bremskraft/-balance anpassen.

### Getriebe
- **`CurrentEngineRpm` vs. `Speed` je Gang:** Fällt die Drehzahl beim Hochschalten unter das
  Powerband → Gänge zu lang gespreizt. Am längsten Geraden-Ende noch weit vom Begrenzer →
  Achsübersetzung länger für mehr Topspeed.
- **Kurvenausgang:** Ist die Drehzahl beim Rausbeschleunigen im kräftigen Bereich? Sonst
  Übersetzung/Gangwahl anpassen.

---

## Merke: abgeleitete Kennzahlen

Der Debrief rechnet aus den Rohfeldern ein paar **Kennzahlen pro Runde/Kurve** aus — das sind die
Zahlen, über die der Ingenieur mit dir spricht:

| Kennzahl | aus | sagt aus |
|---|---|---|
| Balance-Index | `TireSlipAngle` vorne − hinten (in Kurven) | Unter- vs. Übersteuern, mit Vorzeichen |
| Reifentemp-Fenster | `TireTemp` je Rad, Min/Max/Mittel | Druck & Überlastung |
| Federweg-Auslastung | Anteil Zeit nahe `NormalizedSuspensionTravel` 0/1 | Aufsetzen, zu weich/hart |
| Wank-Delta | `NormalizedSuspensionTravel` L−R in Kurven | Stabi-Bedarf |
| Traktions-Events | `TireSlipRatio`-Spitzen beim Gasgeben | Diff/Heck-Traktion |
| Blockier-Events | Raddrehzahl-Einbruch beim Bremsen | Bremsbalance |

➡️ Weiter: [`03-tuning-grundlagen.md`](03-tuning-grundlagen.md)
