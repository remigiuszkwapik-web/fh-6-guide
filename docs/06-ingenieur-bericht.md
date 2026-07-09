# 06 · Den Bericht mit dem Ingenieur nutzen

Das `debrief.py`-Tool auf deinem PC rechnet die Zahlen. Das **Reden** — deuten,
erklären, nachfragen, lehren — macht der Ingenieur (Claude). So läuft die
Übergabe konkret.

## Was du einfügst

Nach dem Debrief hast du eine `bericht.md`. Deren Inhalt fügst du hier im Chat ein
und schreibst **zwei Dinge** dazu:

1. **Was stört dich am meisten?** (dein Bauchgefühl)
2. **Wo in der Kurve?** — Eingang / Mitte / Ausgang, und schnell oder langsam.

Beispiel:
> ```
> [Inhalt von bericht.md eingefügt]
> ```
> „Mich nervt vor allem, dass das Heck am Kurvenausgang aus langsamen Ecken kommt,
> sobald ich Gas gebe."

## Was du zurückbekommst

Der Ingenieur:
1. **bestätigt oder widerlegt** dein Gefühl mit den Zahlen aus dem Bericht,
2. nennt die **wahrscheinliche Ursache**,
3. empfiehlt **genau eine** Änderung — mit **Begründung**, warum diese und nicht eine andere,
4. sagt dir, **worauf du beim Nachmessen achten** sollst.

Rückfragen sind ausdrücklich erwünscht („Warum Stabi und nicht Feder?") — genau
so lernst du das Abstimmen.

## Warum nicht alles das Tool allein macht

Ein Skript kann nur feste „wenn X dann Y"-Sätze ausgeben (das macht `debrief.py`
im Feld *„Automatischer Erst-Vorschlag"* auch schon). Was es **nicht** kann:

- auf deine konkrete Formulierung eingehen,
- mehrere Kennzahlen im Kontext gegeneinander abwägen,
- dir das *Warum* auf deinem Wissensstand erklären,
- deine Rückfragen beantworten.

Deshalb die Aufteilung: **Tool = Messen & Rechnen, Ingenieur = Deuten & Lehren.**

## Guter Prompt-Baustein (optional)

Wenn du willst, dass ich strikt in der Ingenieur-Rolle bleibe, kannst du dem
eingefügten Bericht diesen Satz voranstellen:

> „Sei mein FH6-Renningenieur. Bestätige die Diagnose mit den Zahlen, erklär mir
> das Warum, und schlag genau EINE Änderung vor. Frag nach, wenn dir Infos fehlen."

## Der Loop in einem Bild

```
   record.py ──► debrief.py ──► bericht.md
                                    │  (einfügen + Symptom)
                                    ▼
                              🧑‍🔧 Ingenieur
                          Diagnose · Warum · 1 Änderung
                                    │
                                    ▼
                          Setup ändern (1 Regler)
                                    │
                                    ▼
                          gleiche 2 Runden neu messen ──► zurück zu record.py
```

➡️ Bedienung der Tools: [`../tools/README.md`](../tools/README.md)
