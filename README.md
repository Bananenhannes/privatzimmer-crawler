# privatzimmer-crawler
Sucht die Website des Studentenwerks nach neuen Privatzimmer angeboten ab.

### Vorraussetzungen
Benötigt das twython paket:
`pip install twython`

### Setup
In `Config.py` können die Twitter-api credentials und die mailadresse sowie das passwort eingetragen werden.

### Verwendung
`crawl.py` ausführbar machen: `chmod +x crawl.py`  
Danach kann der crawler gestartet werden: `./crawl.py`
Alternativ mit `python crawl.py` starten.

Der Crawler sucht alle 5 minuten nach neuen Angeboten. Alte bereits gefundene Angebote werden unter `crawlerdata` im JSON format gespeichert.  
Neue Angebote können per mail weitergesendet werden oder an einen twitterbot geschickt werden.  
Wird die Anwendung das erste mal gestartet, wird zunächst versucht die crawlerdata datei zu lesen, falls diese noch nicht existiert wird die liste mit den bereits bestehenden Angeboten initialisiert.
