# Workshop - Einführung IoT mit MQTT

Dieses Repository beinhaltet den Programmcode für den Workshop "Einführung IoT mit MQTT von MAKE IT MINT.

## Benötigte Hardware:
- Broker: Raspberry Pi 3B+/4B/400 mit Raspbian Bullseye
- Clients: Raspberry Pi Pico W oder andere WLAN-fähige Mikrocontroller, auf denen MicroPython installiert werden kann.([Übersicht](https://micropython.org/download/))
- Steckplatinen, Sensoren, Aktuatoren und weitere Bauteile für ausgewählte Clientfunktionen

Für den Broker wird hier eine Raspberry Pi 4B, mit Raspbian Bullseye installiert, verwendet.

Für das Flashen der Mikrocontroller werden Raspberry Pi 400 verwendet. Andere Linuxbetriebssysteme funktionieren aber auch.

## Installation des Brokers (RPi 4B)

Öffne ein Terminal und aktualisiere die verfügbaren Pakete
`sudo apt update`

Installiere Broker und Client
`sudo apt install mosquitto mosquitto-clients`

Der Broker ermöglicht standardmäßig keine Kommunikation nach Außen. Um dies zu ermöglichen muss die Konfigurationsdatei des Broker angepasst werden.

Öffne die Konfigurationsdatei
`sudo nano /etc/mosquitto/mosquitto.conf`

und füge die folgenden Zeilen am Ende der Datei ein

`listener 1883`
`allow_anonymous true`

Drücke STRG + O -> Enter -> STRG + X zum Speichern und Schließen der Datei.

Diese Zeilen legen fest, dass der Broker über Port 1883 mit externen Geräten kommuniziert und auch Geräte ohne Namen zulässt. (Für diesen Workshop notwendig)

Prüfe ob der Broker aktiv ist indem du den folgenden Befehl in der Konsole eingibst
`sudo systemctl status mosquitto.service`
Es sollte ein grünes "(is running)" und weiterer Text angezeigt werden.

UUUUnd der Broker ist einsatzbereit. TOP!

## Mikrocontroller vorbereiten
Dieses Repo beinhaltet die Micropython Firmware für den Raspberry Pi Pico W. [Hier](https://micropython.org/download/rp2-pico-w/) kann überprüft werden, ob eine aktueller Version existiert.

Um die Firmware auf den Pico zu installieren, verbinde den Pico per Mikro-USB Kabel mit dem Raspberry Pi. Ist kein MicroPython installiert, sollte er als USB-Laufwerk mit den beiden Dateien "INDEX.HTM" und "INFO_UF2.TXT" erscheinen.

Falls der Mikrocontroller nicht erscheint, ist bereits eine MicroPython Version installiert und du kannst den Rest dieser Anleitung ignorieren.

    [Optional]
    Willst du die Firmware neu installieren?
    !!ACHTUNG, die folgende Anleitung löscht alle Daten auf dem Mikrocontroller!!
    Dann ziehe das Mikro-USB Kabel wieder ab.
    Halte den "BOOTSEL" Knopf auf dem Pico gedrückt und verbinde währenddessen das Mikro-USB Kabel wieder.
    Nach einigen Sekunden taucht ein neues USB Laufwerk auf.
    Der "BOOTSEL" Knopf kann wieder losgelassen werden.

Sollte keine MicroPython Firmware installiert sein, kopiere die Firmware Datei dieses repos das Laufwerk mit den beiden genannten Dateien.

Jetzt warte en paar Sekunden und \*PLOPP\* das Laufwerk sollte verschwunden sein. Der Mikrocontroller ist jetzt bereit für den Einsatz.

Benutzt du einen anderen Mikrocontroller, befolge bitte die Anleitung zu deiner Hardware auf [dieser](https://micropython.org/download/) Seite.

### Notwendige Python Packages installieren und den Mikrocontroller einrichten
Für diesen Workshop wird die `ampy` Bibliothek von adafruit oder die IDE Thonny (wenn man direkt ein Raspberry Pi für die Programmierung des Pico benutzt) verwendet. Mit beiden Tools kann Code auf dem Mikrocontroller ausgeführt werden.
Die Anleitung für Thonny gibt es in den Workshopunterlagen.

Für `ampy` müssen zuerst die entsprechenden Pthon Pakcages installiert werden. Gib in der Konsole die folgenden Befehle ein.
`pip install adafruit-ampy`
`pip install esptool`

Nur noch zwei Aktionen, dann ist alles bereit.
Öffne die Datei `netzwerk_und_client_einstellungen.py` und Pflege hier die notwendigen Informationen zum Namen deines Mikrocontrollers, der im Netzwerk einzigartig sein sollte, der SSID, dem WLAN Passwort und der IP des Geräts, auf dem der Broker installiert ist.
Die BROKER_IP findest du heraus, indem du auf dem Raspberry Pi mit dem Broker eine Console öffnest und dort den folgenden Befehl eingibst:
`ifconfig -a`
Jetzt sollte viel Text erscheinen und irgendwo dabei die IP Adresse des Geräts stehen. Normalerweise hat sie diese oder eine ähnliche folgende Form
`192.168.1.10`
Trage diesen Wert dann als BROKER_IP ein.

Jetzt kann die `setup_microcontroller.py` Datei des Repositories ausführen. Dabei weren erst die Netzwerk und Client Informationen auf den Pico geschrieben und danach die notwendigen Pakete heruntergeladen.
`pthon setup_microcontroller.py`
Treten hierbei Fehler auf, überprüfe bitte,ob der `PORTNAME` in `setup_microcontroller-py` richtig ist und ob sowohl die SSID und das Passwort stimmen. Das sind die häufigsten Fehler.

Hat alles funktioniert, ist der Pico bereit für sein Leben im IoT Netzwerk :)

### Eigene Skripte ausführen
Eigene Skripte können auf dem Microcontroller auch mit `ampy` ausgeführt werden. Der Befehl `run` führt sie dabei aus, ohne die direkt auf den Microcontroller zu schreiben. Beim entfernen des USB Kabels wird das Skript unterbrochen und nicht wieder neu ausgeführt. Eigene Skripte können mit `ampy` wie folgt ausgeführt werden
`ampy --port "PORTNAME" run "SKRIPTNAME"`
Um zum Beispiel das `ding_vorlage.py` Skript des Repositories auszuführen
`ampy --port dev/ttyACM0 run ding_vorlage.py` 

#### Das wars, es kann losgehen.
Alle weiteren Anleitungsschritte befinden sich in den Workshopunterlagen.