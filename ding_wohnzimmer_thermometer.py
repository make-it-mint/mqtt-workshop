import machine,sys, math
import network
import utime
from umqtt.simple import MQTTClient
from einstellungen import *

#TOPICS
TOPIC_PUBLISHING_MESSUNG = 'WOHNZIMMER/TEMPERATUR/MESSUNG'
TOPIC_PUBLISHING_HEIZUNG_STATUS = 'WOHNZIMMER/HEIZUNG/STATUS'
TOPIC_SUBSCRIPTION_GRENZWERT_ABFRAGE= 'WOHNZIMMER/TEMPERATUR/GRENZWERT_ABFRAGE'

TOPIC_SUBSCRIPTION_GRENZWERT_NEU= 'WOHNZIMMER/TEMPERATUR/GRENZWERT_NEU'
TOPIC_SUBSCRIPTION_INTERVALL= 'WOHNZIMMER/TEMPERATUR/MESSINTERVALL'



#SKRIPTVARIABLEN
MESSINTERVALLIN_SEKUNDEN = 3.0
GRENZWERT_TEMPERATUR=22.0
HEIZUNG_AN=False

#GPIO PINS 
THERMOMETER_PIN = machine.ADC(28)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)

def temperatur_messen():
    temperatur_wert = THERMOMETER_PIN.read_u16()
    Vr = 3.3 * float(temperatur_wert) / 65535
    Rt = 10000 * Vr / (3.3 - Vr)
    temperatur = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
    temperatur_celsius = temperatur - 273.15
    temperatur_fahrenheit = temperatur_celsius * 1.8 + 32
    return round(temperatur_celsius,1)


def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER_IP, keepalive=60)
    client.set_callback(my_callback)
    client.connect()
    print(f'Mit dem MQTT Broker auf IP: {BROKER_IP} verbunden')
    return client


def my_callback(topic, nachricht):
    global GRENZWERT_TEMPERATUR, MESSINTERVALLIN_SEKUNDEN
    print((topic, nachricht))
    try:
        #TEMPERATUR_GRENZWERT VERÄNDERN
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_GRENZWERT_NEU:
            GRENZWERT_TEMPERATUR = float(nachricht.decode("utf-8"))
            print(f"Neuer Grenzwert für Temperatur in Grad Celsius: {GRENZWERT_TEMPERATUR}")

        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_INTERVALL:
            MESSINTERVALLIN_SEKUNDEN = float(nachricht.decode("utf-8"))
            print(f"Neues Messintervall in Sekunden: {MESSINTERVALLIN_SEKUNDEN}")
    except Exception as e:
        print(e)

#Verbidung mit Broker aufbauen
try:
    client = mqtt_connect()
except OSError as e:
    print("Verbindung mit MQTT Broker konnte nicht hergestellt werden")
    sys.exit()

#Subscription Topics auswählen
client.subscribe(TOPIC_SUBSCRIPTION_GRENZWERT_NEU)
client.subscribe(TOPIC_SUBSCRIPTION_INTERVALL)

#Messintervall starten
zuletzt_published_zeit=utime.ticks_ms()
while True:
    #Überprüfen ob neue Inhalte auf den subcribed Topics geschickt wurden
    client.check_msg()

    #Prüfen, ob das Messintervall erreicht ist
    if utime.ticks_diff(utime.ticks_ms(),zuletzt_published_zeit)/1000 > MESSINTERVALLIN_SEKUNDEN:
        #Temperatur messen
        AKTUELLE_TEMPERATUR = temperatur_messen()
        print(f"{AKTUELLE_TEMPERATUR} Grad Celsius gemessen, Grenzwert: {GRENZWERT_TEMPERATUR} Grad Celsius.")
        client.publish(TOPIC_PUBLISHING_MESSUNG, msg=f'{AKTUELLE_TEMPERATUR}')

        #Wenn der Grenzwert überschritten wird, kann etwas ausgeführt werden
        if AKTUELLE_TEMPERATUR <= GRENZWERT_TEMPERATUR:
            HEIZUNG_AN=True
        else:
            HEIZUNG_AN=False

        client.publish(TOPIC_PUBLISHING_HEIZUNG_STATUS, msg=f"{HEIZUNG_AN}")

        #Intervall zurücksetzen
        zuletzt_published_zeit=utime.ticks_ms()


    utime.sleep(.1)