import os
from serial.tools.list_ports import comports as list_comports


meine_comports = [comport.device for comport in list_comports()]
#print(meine_comports)

#Standardport für Raspberry Pi Pico W bei Linux Betriebssystemen (ESP32 hat /dev/ttyUSB0)
PORTNAME='/dev/ttyACM0'

#Überprüfe, ob der Portname richtig ist, ansonsten, fordere zum Ersetzen auf.
if not PORTNAME in meine_comports:
    print(f"""Kein Mikrocontroller am ausgewählten Comport '{PORTNAME}' gefunden.
    Bitte wähle den richtigen Comport aus der folgenden Liste aus
    und ersetze den Wert für PORTNAME in setup_microcontroller.py:\n{meine_comports}""")
else:
    
    #Netzwerkeinstellungen auf den Mikrocontroller hochladen
    os.system(f'ampy --port {PORTNAME} put {os.path.dirname(os.path.abspath(__file__))}/einstellungen.py /einstellungen.py')
    #packages installieren
    os.system(f'ampy --port {PORTNAME} run {os.path.dirname(os.path.abspath(__file__))}/install_libraries.py')

    
    print("Einrichtung abgeschlossen")