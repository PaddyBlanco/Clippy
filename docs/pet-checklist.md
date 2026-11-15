# Prüfliste: Animationen der Klammer

Zum Durchtesten am Gerät. Häufigkeiten und Schwellen stehen in `device/clippy/pet/habits.py` und `senses.py`;
wer dort etwas ändert, passt diese Liste an und setzt den Haken der betroffenen Zeile zurück.

Spalte „Getestet“: ✅ = am Gerät gesehen, ⬜ = noch offen. Stand: 15.11.2026. Nummer 15 (Schlagzeug von selbst) gibt es nicht mehr; sie trommelt nur noch mit.

## Auf Zutun

| Nr. | Getestet | Animation | So provoziert man sie |
|---|---|---|---|
| 1 | ✅ | Begrüßung mit Sprechblase | kommt bei jedem Start |
| 2 | ✅ | Schwindel: Augen kreisen, sie schwankt | Gerät kräftig schütteln (rund 2 von 3 Malen) |
| 3 | ✅ | Umfallen, liegen, aufrappeln | Gerät schütteln, mehrmals versuchen (rund 1 von 3 Malen); dazwischen 4 Sekunden warten |
| 4 | ✅ | Augen rollen mit | Gerät langsam nach links und rechts kippen |
| 5 | ✅ | Finster: wird müde, „I siag nix mehr.“; schwere Lider, entspannte Brauen, blinzelt langsam, Augen fallen zu und gehen mühsam wieder auf | Finger 2 Sekunden auf den Streifen unter dem Display legen und liegen lassen; alle 2,5 bis 5 Sekunden kämpft sie mit dem Schlaf, bis du loslässt; Spruch frühestens alle 10 Sekunden |
| 6 | ✅ | Aufmerken: Brauen hoch | Hand an den Streifen unter dem Display führen; frühestens alle 15 Sekunden, Spruch bei jedem zweiten Mal |
| 7 | ✅ | Ducken und Kopfschütteln | einmal kurz auf die Klammer tippen, ohne den Finger zu bewegen; Streicheln darf es nicht auslösen |
| 8 | ✅ | Richtig grantig: läuft rot an, droht mit dem Drahtende | dreimal innerhalb von 5 Sekunden kurz auf die Klammer tippen, zwischen den Tippern den Finger klar abheben |
| 9 | ✅ | Erschrecken: springt hoch, streckt sich, landet gestaucht | einmal laut klatschen, davor 2 Sekunden still sein |
| 10 | ✅ | Schlagzeug: sie trommelt mit | fünfmal und öfter innerhalb von 2,5 Sekunden aufs Gehäuse oder den Tisch klopfen; hört 1,5 Sekunden nach dem letzten Klopfer auf |
| 11 | ✅ | Unter Strom: Zittern und Blitze | Ladekabel anstecken; nur einmal, nicht wieder, solange der Akku lädt |
| 22 | ✅ | Streicheln: Augen zu, sie wiegt sich | Finger auf die Klammer legen und liegen lassen oder darüber streichen, auch mehrmals kurz hintereinander; hört auf, sobald du loslässt. Gegenprobe: schnell hintereinander auf sie tippen ist kein Streicheln, sie duckt sich und wird grantig |
| 27 | ✅ | Auf dem Kopf: Desktop dreht sich, sie fällt auf den Kopf, rollt nach rechts an ihren Platz, läuft rot an und beschwert sich | Gerät auf den Kopf stellen und kurz halten; danach wieder zurückdrehen, das Gleiche noch einmal. Tippen auf Symbole und die Klammer muss danach weiter stimmen |
| 28 | ⬜ | Agent arbeitet: merkt auf, schaut gespannt zur Seite, gelbes Kästchen in der Taskleiste | Claude Code, Codex oder Copilot am PC etwas fragen (Einrichten: [agent-hooks.md](agent-hooks.md)) |
| 29 | ⬜ | Agent wartet: hüpft, winkt, „… braucht di!“, rotes Kästchen; nach 30 und 60 s noch einmal, dann nur noch das rote Kästchen | den Agent etwas tun lassen, das eine Freigabe braucht; einmal auf die Klammer tippen, dann ruft sie nicht mehr |
| 30 | ⬜ | Agent fertig: springt vor Freude, grünes Kästchen | Antwort des Agents abwarten |
| 31 | ⬜ | Kästchen verschwindet | Sitzung des Agents beenden |
| 12 | ✅ | Aufwachen | irgendetwas aus 2 bis 10 tun, während sie schläft |

## Von selbst

| Nr. | Getestet | Animation | Wann |
|---|---|---|---|
| 13 | ✅ | Blinzeln | alle 2,5 bis 6 Sekunden |
| 14 | ✅ | Umschauen | nach 6 Sekunden, dann alle 8 bis 20 Sekunden |
| 16 | ✅ | Bizepscurls mit Hantel | nach 1 Minute, dann alle 3 bis 6 Minuten |
| 24 | ✅ | Anlehnen: lehnt sich kurz rechts an den Bildschirmrand | nach rund 40 Sekunden, dann alle 2 bis 5 Minuten |
| 25 | ✅ | Will Aufmerksamkeit: hüpft hin und her und winkt | wenn 1 Minute lang nichts aus 2 bis 10 passiert ist, dann alle 2 bis 4 Minuten |
| 17 | ✅ | Langeweile: je Mal eines davon: Augen verdrehen, strecken, Schlagzeug-Solo, Hanteln, auf den Kopf rollen und zurück, Pogo auf dem Drahtende | wenn 1 Minute lang nichts aus 2 bis 10 passiert ist, dann alle 15 bis 30 Sekunden; sie schläft dabei nicht ein |
| 18 | ✅ | Sekundenschlaf: sackt ab, schreckt hoch | Sensor unter dem Display zuhalten, nach rund 20 Sekunden; nachts nach 1,5 Minuten Ruhe |
| 19 | ✅ | Einschlafen: Augen ganz zu, Zs steigen auf und treiben davon, sie atmet, Display dimmt | Sensor zuhalten, nach rund 40 Sekunden; nachts nach 3 Minuten, im dunklen Raum nach 5 Minuten Ruhe; loslassen weckt sie |
| 26 | ✅ | Display wird dunkler | Sensor unter dem Display 2 Sekunden zuhalten; nach dem Loslassen wieder hell |
| 23 | ✅ | Rotzblase im Schlaf, wächst und schrumpft mit dem Atem | bei jedem zehnten Einschlafen, also Glückssache; zum Testen `SNOT_CHANCE` in `habits.py` kurz auf 1 stellen |

Bei 16, 17, 18 und 25 sagt sie bei jedem zweiten Mal etwas dazu. Für 17 und 25 das Gerät nicht berühren und leise sein,
für 18 und 19 nur den Sensor zuhalten und sonst nichts tun; jedes Ereignis lässt die Wartezeit von vorn beginnen.
Für 17 jede der sechs Beschäftigungen einmal sehen; welche kommt, ist Zufall.

## Schwer zu provozieren

| Nr. | Getestet | Animation | Wann |
|---|---|---|---|
| 20 | ⬜ | Hunger: Gähnen und Spruch | Akku unter 15 % und kein Kabel dran |
| 21 | ✅ | Müde Lider (Augen halb zu) | zwischen 23 und 6 Uhr |
