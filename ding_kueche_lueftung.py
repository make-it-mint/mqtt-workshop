import machine,sys
import network
import utime
from umqtt.simple import MQTTClient
from einstellungen import *


#TOPICS
TOPIC_PUBLISHING_LUEFTUNG = 'KUECHE/LUEFTUNG/LUEFTUNG_STATUS'

TOPIC_SUBSCRIPTION_LUEFTUNG_SCHALTEN = 'KUECHE/LUEFTUNG/SCHALTEN'
TOPIC_SUBSCRIPTION_STATUS_ABFRAGE= 'KUECHE/LUEFTUNG/STATUS_ABFRAGE'

#SKRIPTVARIABLEN
LUEFTUNG_AN=False

#GPIO PINS 
LUEFTUNG_PIN = machine.Pin(16, machine.Pin.OUT, machine.Pin.PULL_DOWN)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)



def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER_IP, keepalive=60)
    client.set_callback(my_callback)
    client.connect()
    print(f'Mit dem MQTT Broker auf IP: {BROKER_IP} verbunden')
    return client


def my_callback(topic, nachricht):
    global LUEFTUNG_AN
    print((topic, nachricht))
    try:
        #TEMPERATUR_GRENZWERT VERÄNDERN
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_LUEFTUNG_SCHALTEN:
            if LUEFTUNG_AN:
                LUEFTUNG_AN = False
                LUEFTUNG_PIN.off()
            else:
                LUEFTUNG_AN = True
                LUEFTUNG_PIN.on()
            client.publish(TOPIC_PUBLISHING_LUEFTUNG, msg=f'{LUEFTUNG_AN}')

        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_STATUS_ABFRAGE:
            client.publish(TOPIC_PUBLISHING_LUEFTUNG, msg=f'{LUEFTUNG_AN}')

    except Exception as e:
        print(e)

#Verbidung mit Broker aufbauen
try:
    client = mqtt_connect()
except OSError as e:
    print("Verbindung mit MQTT Broker konnte nicht hergestellt werden")
    sys.exit()

#Subscription Topics auswählen
client.subscribe(TOPIC_SUBSCRIPTION_LUEFTUNG_SCHALTEN)
client.subscribe(TOPIC_SUBSCRIPTION_STATUS_ABFRAGE)

#Messintervall starten
zuletzt_published_zeit=utime.ticks_ms()
while True:
    #Überprüfen ob neue Inhalte auf den subcribed Topics geschickt wurden
    client.check_msg()
    print("Neue Abfrage")

    utime.sleep(.1)