import machine,sys
import network
import utime
from umqtt.simple import MQTTClient
from einstellungen import *





#TOPICS
TOPIC_PUBLISHING_HELLIGKEIT = 'WOHNZIMMER/HELLIGKEIT/HELLIGKEIT_AKTUELL'
TOPIC_PUBLISHING_GRENZWERT= 'WOHNZIMMER/HELLIGKEIT/GRENZWERT_AKTUELL'
TOPIC_PUBLISHING_LED_STATUS = 'WOHNZIMMER/HELLIGKEIT/LED_STATUS'


TOPIC_SUBSCRIPTION_LED = 'WOHNZIMMER/HELLIGKEIT/LED_ABFRAGE'
TOPIC_SUBSCRIPTION_GRENZWERT_NEU= 'WOHNZIMMER/HELLIGKEIT/GRENZWERT_NEU'
TOPIC_SUBSCRIPTION_GRENZWERT_ABFRAGE= 'WOHNZIMMER/HELLIGKEIT/GRENZWERT_ABFRAGE'

#SKRIPTVARIABLEN
MESSINTERVALLIN_SEKUNDEN = 3.0
GRENZWERT_HELLIGKEIT=0.4
LED_AN=False
AKTUELLE_HELLIGKEIT=0.0

#GPIO PINS 
LED = machine.Pin("LED", machine.Pin.OUT, value=0)
PIN_PHOTOWIDERSTAND = machine.ADC(0)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	utime.sleep(1)

def helligkeit_messen():
    #Gibt einen Helligkeitswert zwischen 0 und 1 zurück. z.B. 0.15 oder 0.3
    #Der Wert sinkt mit zunehmender Helligkeit
    return round((1-int(PIN_PHOTOWIDERSTAND.read_u16())/65535),2)


def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER_IP, keepalive=60)
    client.set_callback(my_callback)
    client.connect()
    print(f'Mit dem MQTT Broker auf IP: {BROKER_IP} verbunden')
    return client


def my_callback(topic, nachricht):
    global GRENZWERT_HELLIGKEIT
    print((topic, nachricht))
    try:
        #LED per Topic an und aus schalten
        if topic.decode("utf-8") == TOPIC_SUBSCRIPTION_GRENZWERT_NEU:     
            nachricht = nachricht.decode("utf-8")
            GRENZWERT_HELLIGKEIT = float(nachricht)
            client.publish(TOPIC_PUBLISHING_GRENZWERT, msg=f'{GRENZWERT_HELLIGKEIT}')
            print(f"Neuer Grenzwert gesetzt: {GRENZWERT_HELLIGKEIT}")

        #TEMPERATUR_GRENZWERT VERÄNDERN
        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_LED:
            client.publish(TOPIC_PUBLISHING_LED_STATUS, msg=f'{LED_AN}')
            print(f"LED Status gepublished")

        elif topic.decode("utf-8") == TOPIC_SUBSCRIPTION_GRENZWERT_ABFRAGE:
            client.publish(TOPIC_PUBLISHING_GRENZWERT, msg=f'{GRENZWERT_HELLIGKEIT}')
            print(f"Aktuellen Grenzwert gepublished")
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
client.subscribe(TOPIC_SUBSCRIPTION_GRENZWERT_NEU)
client.subscribe(TOPIC_SUBSCRIPTION_GRENZWERT_ABFRAGE)

#Messintervall starten
zuletzt_published_zeit=utime.ticks_ms()
client.publish(TOPIC_PUBLISHING_HELLIGKEIT, msg=f'{helligkeit_messen()}')
client.publish(TOPIC_PUBLISHING_LED_STATUS, msg=f'{LED_AN}')



while True:
    #Überprüfen ob neue Inhalte auf den subcribed Topics geschickt wurden
    client.check_msg()

    #Prüfen, ob das Messintervall erreicht ist
    if utime.ticks_diff(utime.ticks_ms(),zuletzt_published_zeit)/1000 > MESSINTERVALLIN_SEKUNDEN:
        #Helligkeit messen
        AKTUELLE_HELLIGKEIT = helligkeit_messen()
        print(f"{AKTUELLE_HELLIGKEIT} für Helligkeit gemessen, Grenzwert: {GRENZWERT_HELLIGKEIT}")
        client.publish(TOPIC_PUBLISHING_HELLIGKEIT, msg=f'{AKTUELLE_HELLIGKEIT}')

        #Wenn der Grenzwert überschritten ist, aktuelle Temperatur Pulishen
        if AKTUELLE_HELLIGKEIT <= GRENZWERT_HELLIGKEIT and not LED_AN:
            LED_AN = True
            LED.on()
            client.publish(TOPIC_PUBLISHING_LED_STATUS, msg=f'{LED_AN}')
        elif AKTUELLE_HELLIGKEIT > GRENZWERT_HELLIGKEIT and LED_AN:
            LED_AN = False
            LED.off()
            client.publish(TOPIC_PUBLISHING_LED_STATUS, msg=f'{LED_AN}')


        #Intervall zurücksetzen
        zuletzt_published_zeit=utime.ticks_ms()


    utime.sleep(.1)