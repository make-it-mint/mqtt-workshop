import network
import time
import upip
from einstellungen import *


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PASSWORT)
print(wlan.status())
while not wlan.isconnected() and wlan.status() >= 0:
	print("Verbinde...")
	time.sleep(1)
print(wlan.status())
upip.install('umqtt.simple')
