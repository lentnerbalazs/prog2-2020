
A mi értelmezésünk és kérdésfeltevéseink egy olyan adatbázisra épültek, melyet a megadott adatokból össze lehet építeni, ám valójában 
sokkal több, sokrétűbb és színesebb adatra lenne szükségünk ahhoz, hogy optimális válaszokat tudjunk belőle adni.
Valami előrejelzés a következő meccsekre
A jelenlegi oldalban van egy hasonló feature, amellyel az ügyfelek megnézhetik a beágyazott szorzókat a soron következő meccsekre, 
amihez adatokat szolgűltat az oldal, hogy pl. hogyan szerepelt egyik/másik csapat az elmúlt x meccsén, vagy hány gólt szereztek ez ellen a csapat ellen múltkor.
Ennek lenne egy továbbfejlesztése egy olyan előrejelzés, ami ezen és hasonló adatok alapján mondana egy becslést a meccs kimenetelét illetően.
- ehhez szükség van:
	a tabellára (vagy valami hasonlóan disztingváló listára)
	egymás elleni korábbi meccsek eredményeire
	elmúlt időszak eredményessége valahogy mérve
És végeredményben kapnánk egy - a whoscore pontozási rendszeréhez hasonló - belsős adatokból becsült értéket.

Mennyire kompatibilis egy játékos egy csapattal?
Ez a feature elsősorban játékra lenne alkalmas (vagy ha valóban jó előrejelzést készít, akkor a kluboknak segíteni transzferek előtt)
A foci egy csapatsport és a játékosok "individuális" teljesítménye valójában mindig kontextusban van értelmezve (csapat, edző, trénerek, drukkerek).
A basic koncepció a feature mögött, hogy szeretnénk a játékos teljesítményét függetleníteni ezen tényezőktől.
Ennek egyik formája lenne, hogy az alábbi kérdést próbáljuk megválaszolni:
- Ha kivesszük a vele egy csapatban játszó jó játékosokat, akkor azon meccseken historikusan hogyan játszott a vizsgált játékos?
	Ehhez kell a játékosok scorejai (whoscore pontozási rendszer)
	Historikus meccs adatok
Ezek alapján - megfelelő mennyiségű adat mellett - lehetne vizsgálni, hogy a játékos mennyiben függ a többi jó játékos játékától, illetve mennyire tud önállóan érvényesülni.
Másik vizsgálandó kérdés lenne:
- Ha beteszünk egy játékost egy másik csapatba, akkor hogy fog teljesíteni?
	Biró-Szabó féle harmónia index
	Kémia-score
	Whoscore scoring rendszerébe beépítünk/módosítjuk plusz faktorokat (együttműködést mérik)
	Csapatinfók
Ennek az alapgondolata a FIFA Ultimate Team volt, ahol is több kvalitatív kooperációs tényezőt is vizsgál a játék a csaptösszeállítás során. 
Az előző kérdésen felül itt egy játékos sikerességét megpróbálnánk kontextusban értelmezni, de a szinergia hatások definiálásával, azaz, hogy pl. a bal láb, a sok futás és a hosszú 
passzok eredménye, hogy jól játszik össze egy másik játékossal.[Ennek kivitelezhető változata, hogy azt mondjuk, hogy historikusan x csatár akkor játszott jól, ha azon a meccsen a 
csatársor score-ja kb 82,5 pont volt kis szórással és a középpálya pedig minimum 60 score-os.]
Egy érdekes kérdés lehetne még, hogy egy játékos teljesítményét egy másik csapat ellen próbáljuk meghatározni. Itt szintén érdemes minél inkább individuális skillekkel dolgozni,
amit mondjuk az első kérdés megválaszolása során nyerünk ki.
Ehhez pluszba kellenek még az alábbi adatok:
	Historikus meccsadatok
	Player - védősor reláció összehasonlítása pl

Az ultimate kérdés pedig a fentebbi két kérdés kombinációja, ami nagyon menő lenne ha valaha is megválaszolásra kerülne :)
- Egy játékos egy adott csapat tagjaként milyen hatékonysággal fog játszani egy adott csapat ellen?
	Ugyanazon adatbázis használata, mint amit korábbi kérdésekre használtunk elméletben
