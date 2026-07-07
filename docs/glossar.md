# Glossar

Kurz und praxisnah. Details stehen in den jeweiligen Kapiteln.

| Begriff | Bedeutung |
|---|---|
| **Data Out** | Forzas UDP-Telemetrie-Ausgabe. Sendet ~60x/s ein Datenpaket an eine IP/Port. |
| **UDP** | Netzwerkprotokoll ohne Rückkanal — „abschicken und vergessen". Ideal für schnelle Telemetrie. |
| **Paket** | Ein einzelner Telemetrie-Datensatz (ein Physik-Tick), z. B. 331 Bytes im Dash-Format. |
| **Sled / Dash** | Zwei Paketformate. „Sled" = nur Physik-Grunddaten. „Dash" = voll, inkl. Reifentemps, Leistung, Runden. **Immer Dash nutzen.** |
| **little-endian** | Byte-Reihenfolge, in der Zahlen im Paket liegen (niedrigstes Byte zuerst). Wichtig fürs Parsen. |
| **IsRaceOn** | Flag: 1 = Rennen/Physik aktiv. Nur solche Pakete auswerten. |
| **FL/FR/RL/RR** | Radreihenfolge: vorne-links, vorne-rechts, hinten-links, hinten-rechts. |
| **Untersteuern** | Front hat weniger Grip, Auto „schiebt" geradeaus. Telemetrie: SlipAngle vorne > hinten. |
| **Übersteuern** | Heck hat weniger Grip, Auto dreht ein / bricht aus. Telemetrie: SlipAngle hinten > vorne. |
| **Schräglaufwinkel (Slip Angle)** | Winkel zwischen Blickrichtung und tatsächlicher Rollrichtung des Reifens — Maß für Quer-Grip-Ausnutzung. |
| **Schlupf / Slip Ratio** | Längs-Schlupf: Verhältnis Raddrehzahl zu Fahrgeschwindigkeit. >0 durchdrehend, <0 blockierend. |
| **Combined Slip** | Gesamtschlupf (längs + quer). ~>1 = jenseits des Grip-Limits. |
| **Gierrate (Yaw rate)** | Drehgeschwindigkeit ums Hochachse (AngularVelocity.Y). Wie schnell das Auto einlenkt. |
| **Federweg (Suspension Travel)** | Wie weit die Feder eingefedert ist. Normiert 0 (aus) … 1 (Anschlag). |
| **Wank-Delta** | Federweg-Differenz L−R einer Achse in der Kurve = Maß fürs Wanken. |
| **Stabilisator (ARB)** | Antiroll Bar; verbindet L/R einer Achse. Wichtigstes Balance-Werkzeug ohne Geraden-Nebenwirkung. |
| **Federrate** | Kraft, mit der die Feder der Last widersteht (Steifigkeit). |
| **Dämpfer: Bump/Rebound** | Tempo der Federbewegung. Bump = Einfedern, Rebound = Ausfedern. |
| **Sturz (Camber)** | Radneigung von vorn gesehen. Negativ = oben nach innen → mehr Kurvengrip. |
| **Spur (Toe)** | Radausrichtung von oben. Toe-out = schärferes Einlenken, Toe-in = Stabilität. |
| **Nachlauf (Caster)** | Neigung der Lenkachse. Mehr = mehr Geradeausstabilität + dynamischer Sturz. |
| **Downforce** | Aerodynamischer Anpressdruck. Wirkt v. a. bei hohem Tempo; Front/Heck = Balance-Werkzeug. |
| **Differenzial (Diff)** | Verteilt Antriebsmoment L/R. Accel = unter Gas, Decel = im Schub. Traktion & Balance am Kurvenausgang. |
| **Final Drive** | Achsübersetzung. Kürzer = mehr Beschleunigung, länger = mehr Topspeed. |
| **Balance-Index** | Abgeleitete Kennzahl: SlipAngle vorne − hinten. Vorzeichen = Unter-/Übersteuern. |
| **Debrief** | Nachbesprechung nach den Messrunden: Diagnose + eine begründete Änderung. |
| **Drivetrain (FWD/RWD/AWD)** | Front-/Heck-/Allradantrieb. Bestimmt viele Diff- und Balance-Entscheidungen. |
| **PI (Performance Index)** | Forzas Leistungswert (Klassen D–X). Manche Tunes zielen auf einen PI-Deckel. |
