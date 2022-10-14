import machine, sys
import network
import utime
from umqtt.simple import MQTTClient
from einstellungen import *


#TOPICS
TOPIC_PUBLISHING_ALARMSTUFE = 'KUECHE/FEUERALARM/WARNUNG'

TOPIC_SUBSCRIPTION_FEUCHTIGKEIT = 'KUECHE/LUFTFEUCHTIGKEIT/LUFTFEUCHTIGKEIT_AKTUELL'
TOPIC_SUBSCRIPTION_TEMPERATUR= 'KUECHE/TEMPERATUR/TEMPERATUR_AKTUELL'

#SKRIPTVARIABLEN
AKTUELLE_TEMPERATUR = 0.0
AKTUELLE_LUFTFEUCHTE = 80.0
PUBLISH_INTERVALL_IN_SEKUNDEN = 3.0

WARNSTUFE = 0
#Grenzwerte (TEMPERATUR,LUFTFEUCHTE)
GRENZWERT_BEOBACHTUNG = (40,50) # WARNSTUFE = 1
GRENZWERT_WARNUNG = (60,40) # WARNSTUFE = 2
GRENZWERT_ALARM = (80,20) # WARNSTUFE = 3

#GPIO PINS 
PIEPER_PIN = machine.Pin(15, machine.Pin.OUT, machine.Pin.PULL_DOWN)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)

def warnstufe_bestimmen():
    if AKTUELLE_TEMPERATUR >= GRENZWERT_ALARM[0] and AKTUELLE_LUFTFEUCHTE <= GRENZWERT_ALARM[1]:
        return 3
    elif AKTUELLE_TEMPERATUR >= GRENZWERT_WARNUNG[0] and AKTUELLE_LUFTFEUCHTE <= GRENZWERT_WARNUNG[1]:
        return 2
    elif AKTUELLE_TEMPERATUR >= GRENZWERT_BEOBACHTUNG[0] and AKTUELLE_LUFTFEUCHTE <= GRENZWERT_BEOBACHTUNG[1]:
        return 1
    else:
        return 0


def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER_IP, keepalive=60)
    client.set_callback(my_callback)
    client.connect()
    print(f'Mit dem MQTT Broker auf IP: {BROKER_IP} verbunden')
    return client


def my_callback(topic, nachricht):
    global AKTUELLE_TEMPERATUR, AKTUELLE_LUFTFEUCHTE
    print((topic, nachricht))
    try:
        #TEMPERATUR_GRENZWERT VERÄNDERN
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_TEMPERATUR:
            AKTUELLE_TEMPERATUR = nachricht.decode("utf-8")
            print(f"Aktuelle Temperatur: {AKTUELLE_TEMPERATUR}°C")

        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_FEUCHTIGKEIT:
            AKTUELLE_LUFTFEUCHTE = nachricht.decode("utf-8")
            print(f"Aktuelle Luftfeuchtigkeit: {AKTUELLE_LUFTFEUCHTE}%")
    except Exception as e:
        print(e)

#Verbidung mit Broker aufbauen
try:
    client = mqtt_connect()
except OSError as e:
    print("Verbindung mit MQTT Broker konnte nicht hergestellt werden")
    sys.exit()

#Subscription Topics auswählen
client.subscribe(TOPIC_SUBSCRIPTION_TEMPERATUR)
client.subscribe(TOPIC_SUBSCRIPTION_FEUCHTIGKEIT)

#Messintervall starten
zuletzt_published_zeit=utime.ticks_ms()
while True:
    #Überprüfen ob neue Inhalte auf den subcribed Topics geschickt wurden
    client.check_msg()

    #Prüfen, ob das Messintervall erreicht ist
    if utime.ticks_diff(utime.ticks_ms(),zuletzt_published_zeit)/1000 > PUBLISH_INTERVALL_IN_SEKUNDEN:
        #WARNSTUFE_BESTIMMEN
        WARNSTUFE = warnstufe_bestimmen()
        print(f"Aktuelle Warnstufe: {WARNSTUFE}")
        client.publish(TOPIC_PUBLISHING_ALARMSTUFE, msg=f'{WARNSTUFE}')

        #Intervall zurücksetzen
        zuletzt_published_zeit=utime.ticks_ms()

        #Warnpieper schalten
        if WARNSTUFE == 1:
            PIEPER_PIN.on()
            utime.sleep(0.5)
            PIEPER_PIN.off()
            PUBLISH_INTERVALL_IN_SEKUNDEN = 3.0
        elif WARNSTUFE == 2:
            PIEPER_PIN.on()
            utime.sleep(0.5)
            PIEPER_PIN.off()
            PUBLISH_INTERVALL_IN_SEKUNDEN = 1.0
        elif WARNSTUFE == 3:
            PIEPER_PIN.on()
            PUBLISH_INTERVALL_IN_SEKUNDEN = 0.5
        else:
            PIEPER_PIN.off()
            PUBLISH_INTERVALL_IN_SEKUNDEN = 3.0

        


    utime.sleep(.1)