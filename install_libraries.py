import network
import time
import upip
from netzwerk_und_client_einstellungen import *


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)

while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	time.sleep(1)

upip.install('umqtt.simple')
