# Prüfliste: Animationen der Klammer

Zum Durchtesten am Gerät. Häufigkeiten und Schwellen stehen in `device/clippy/pet/habits.py` und `senses.py`;
wer dort etwas ändert, passt diese Liste an und setzt den Haken der betroffenen Zeile zurück.

Spalte „Getestet“: ✅ = am Gerät gesehen, ⬜ = noch offen. Stand: 12.11.2026. Nummer 15 (Schlagzeug von selbst) gibt es nicht mehr; sie trommelt nur noch mit.

## Auf Zutun

| Nr. | Getestet | Animation | So provoziert man sie |
|---|---|---|---|
| 1 | ✅ | Begrüßung mit Sprechblase | kommt bei jedem Start |
| 2 | ✅ | Schwindel: Augen kreisen, sie schwankt | Gerät kräftig schütteln (rund 2 von 3 Malen) |
| 3 | ✅ | Umfallen, liegen, aufrappeln | Gerät schütteln, mehrmals versuchen (rund 1 von 3 Malen); dazwischen 4 Sekunden warten |
| 4 | ✅ | Augen rollen mit | Gerät langsam nach links und rechts kippen |
| 5 | ✅ | Grantig: läuft rot an, „Finster is!“ | Finger auf den Streifen unter dem Display legen; frühestens alle 10 Sekunden |
| 6 | ✅ | Aufmerken: Brauen hoch | Hand an den Streifen unter dem Display führen; frühestens alle 15 Sekunden, Spruch bei jedem zweiten Mal |
| 7 | ✅ | Ducken und Kopfschütteln | einmal kurz auf die Klammer tippen |
| 8 | ✅ | Richtig grantig: läuft rot an, droht mit dem Drahtende | dreimal innerhalb von 5 Sekunden kurz auf die Klammer tippen, zwischen den Tippern den Finger klar abheben |
| 9 | ✅ | Erschrecken: springt hoch, streckt sich, landet gestaucht | einmal laut klatschen, davor 2 Sekunden still sein |
| 10 | ✅ | Schlagzeug: sie trommelt mit | dreimal und öfter zügig aufs Gehäuse oder den Tisch klopfen; hört 1,5 Sekunden nach dem letzten Klopfer auf |
| 11 | ✅ | Unter Strom: Zittern und Blitze | Ladekabel anstecken; danach alle 20 bis 40 Sekunden wieder, solange der Akku lädt |
| 22 | ✅ | Streicheln: Augen zu, sie wiegt sich | Finger auf die Klammer legen und liegen lassen oder darüber streichen; hört auf, sobald du loslässt |
| 12 | ✅ | Aufwachen | irgendetwas aus 2 bis 10 tun, während sie schläft |

## Von selbst

| Nr. | Getestet | Animation | Wann |
|---|---|---|---|
| 13 | ✅ | Blinzeln | alle 2,5 bis 6 Sekunden |
| 14 | ✅ | Umschauen | nach 6 Sekunden, dann alle 8 bis 20 Sekunden |
| 16 | ✅ | Bizepscurls mit Hantel | nach 1 Minute, dann alle 3 bis 6 Minuten |
| 24 | ✅ | Anlehnen: lehnt sich kurz rechts an den Bildschirmrand | nach rund 40 Sekunden, dann alle 2 bis 5 Minuten |
| 25 | ✅ | Will Aufmerksamkeit: hüpft hin und her und winkt | wenn 1 Minute lang nichts aus 2 bis 10 passiert ist, dann alle 2 bis 4 Minuten |
| 17 | ✅ | Langeweile: Augen verdrehen | wenn 2 Minuten lang nichts aus 2 bis 10 passiert ist |
| 18 | ✅ | Sekundenschlaf: sackt ab, schreckt hoch | wenn 3,5 Minuten lang nichts passiert ist |
| 19 | ✅ | Einschlafen: Augen zu, Zs steigen auf und treiben davon, sie atmet, Display dimmt | nach 5 Minuten Ruhe, nur wenn es dunkel ist; nachts nach 3 Minuten |
| 23 | ✅ | Rotzblase im Schlaf, wächst und schrumpft mit dem Atem | bei jedem zehnten Einschlafen, also Glückssache; zum Testen `SNOT_CHANCE` in `habits.py` kurz auf 1 stellen |

Bei 16, 17, 18 und 25 sagt sie bei jedem zweiten Mal etwas dazu. Für 17 bis 19 und 25 das Gerät nicht berühren und leise sein,
sonst beginnt die Wartezeit von vorn.

## Schwer zu provozieren

| Nr. | Getestet | Animation | Wann |
|---|---|---|---|
| 20 | ⬜ | Hunger: Gähnen und Spruch | Akku unter 15 % und kein Kabel dran |
| 21 | ✅ | Müde Lider (Augen halb zu) | zwischen 23 und 6 Uhr |
