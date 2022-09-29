import machine,sys
import network
import utime
from umqtt.simple import MQTTClient
from netzwerk_und_client_einstellungen import *

#TOPICS
TOPIC_PUBLISHING = 'WOHNZIMMER/TEMPERATUR/MESSUNG'
TOPIC_SUBSCRIPTION_LED = 'WOHNZIMMER/TEMPERATUR/LED_STATUS'
TOPIC_SUBSCRIPTION_GRENZE= 'WOHNZIMMER/TEMPERATUR/GRENZWERT'
TOPIC_SUBSCRIPTION_INTERVALL= 'WOHNZIMMER/TEMPERATUR/MESSINTERVALL'

#SKRIPTVARIABLEN
MESSINTERVALLIN_SEKUNDEN = 5.0
GRENZWERT_TEMPERATUR=27.0
LED_ON=False

#GPIO PINS 
led = machine.Pin("LED", machine.Pin.OUT)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)

def temperatur_messen():
    #TODO Temperatur Messen Code
    return 20


def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER_IP, keepalive=60)
    client.set_callback(my_callback)
    client.connect()
    print(f'Mit dem MQTT Broker auf IP: {BROKER_IP} verbunden')
    return client


def my_callback(topic, nachricht):
    global GRENZWERT_TEMPERATUR, MESSINTERVALLIN_SEKUNDEN, LED_ON, led
    print((topic, nachricht))
    try:
        #LED per Topic an und aus schalten
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_LED:     
            nachricht = nachricht.decode("utf-8")
            LED_ON = True if nachricht == "True" or nachricht == "1" else False
            led.on() if LED_ON else led.off()

        #TEMPERATUR_GRENZWERT VERÄNDERN
        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_GRENZE:
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
client.subscribe(TOPIC_SUBSCRIPTION_LED)
client.subscribe(TOPIC_SUBSCRIPTION_GRENZE)
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

        #Wenn der Grenzwert überschritten ist, aktuelle Temperatur Pulishen
        if AKTUELLE_TEMPERATUR >= GRENZWERT_TEMPERATUR:
            client.publish(TOPIC_PUBLISHING, msg=f'{AKTUELLE_TEMPERATUR}')

        #Intervall zurücksetzen
        zuletzt_published_zeit=utime.ticks_ms()


    utime.sleep(.1)