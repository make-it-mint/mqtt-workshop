import machine, sys
import network
import utime
from dht import DHT22
from umqtt.simple import MQTTClient
from einstellungen import *


#TOPICS
TOPIC_PUBLISHING_TEMPERATUR = 'KUECHE/TEMPERATUR/TEMPERATUR_AKTUELL'
TOPIC_PUBLISHING_LUFTFEUCHTIGKEIT= 'KUECHE/LUFTFEUCHTIGKEIT/LUFTFEUCHTIGKEIT_AKTUELL'

TOPIC_SUBSCRIPTION_FEUCHTIGKEIT_ABFRAGE = 'KUECHE/LUFTFEUCHTIGKEIT/FEUCHTIGKEIT_ABFRAGE'
TOPIC_SUBSCRIPTION_TEMPERATUR_ABFRAGE= 'KUECHE/TEMPERATUR/TEMPERATUR_ABFRAGE'

#SKRIPTVARIABLEN
MESSINTERVALLIN_SEKUNDEN = 3.0
AKTUELLE_TEMPERATUR = 20.0
AKTUELLE_LUFTFEUCHTE = 60.0

#GPIO PINS 
DHT22_SENSOR = DHT22(machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP))


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)

def luft_messen():
    DHT22_SENSOR.measure()
    temperatur = DHT22_SENSOR.temperature()
    luftfeuchte = DHT22_SENSOR.humidity()
    return temperatur, luftfeuchte
    #return round(random.uniform(0,100),2), round(random.uniform(0,100),2)


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
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_TEMPERATUR_ABFRAGE:
            AKTUELLE_TEMPERATUR, AKTUELLE_LUFTFEUCHTE = luft_messen()
            client.publish(TOPIC_PUBLISHING_TEMPERATUR, msg=f'{AKTUELLE_TEMPERATUR}')
            print(f"Temperatur gepublished")

        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_FEUCHTIGKEIT_ABFRAGE:
            AKTUELLE_TEMPERATUR, AKTUELLE_LUFTFEUCHTE = luft_messen()
            client.publish(TOPIC_PUBLISHING_LUFTFEUCHTIGKEIT, msg=f'{AKTUELLE_LUFTFEUCHTE}')
            print(f"Luftfeuchtigkeit gepublished")
    except Exception as e:
        print(e)

#Verbidung mit Broker aufbauen
try:
    client = mqtt_connect()
except OSError as e:
    print("Verbindung mit MQTT Broker konnte nicht hergestellt werden")
    sys.exit()

#Subscription Topics auswählen
client.subscribe(TOPIC_SUBSCRIPTION_FEUCHTIGKEIT_ABFRAGE)
client.subscribe(TOPIC_SUBSCRIPTION_TEMPERATUR_ABFRAGE)

#Messintervall starten
zuletzt_published_zeit=utime.ticks_ms()
while True:
    #Überprüfen ob neue Inhalte auf den subcribed Topics geschickt wurden
    client.check_msg()

    #Prüfen, ob das Messintervall erreicht ist
    if utime.ticks_diff(utime.ticks_ms(),zuletzt_published_zeit)/1000 > MESSINTERVALLIN_SEKUNDEN:
        #Luft messen
        AKTUELLE_TEMPERATUR, AKTUELLE_LUFTFEUCHTE = luft_messen()
        print(f"Aktuelle Luftfeuchtigkeit: {AKTUELLE_LUFTFEUCHTE}%, Aktuelle Temperatur: {AKTUELLE_TEMPERATUR}°C")
        client.publish(TOPIC_PUBLISHING_TEMPERATUR, msg=f'{AKTUELLE_TEMPERATUR}')
        client.publish(TOPIC_PUBLISHING_LUFTFEUCHTIGKEIT, msg=f'{AKTUELLE_LUFTFEUCHTE}')


        #Intervall zurücksetzen
        zuletzt_published_zeit=utime.ticks_ms()


    utime.sleep(.1)