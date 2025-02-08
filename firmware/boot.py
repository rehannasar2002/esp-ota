# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

import network
import time
import machine

ssid = "Shivoham"
password = "9705096919"

# Blue LED
led = machine.Pin(2, machine.Pin.OUT)
led2 = machine.Pin(2, machine.Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        print("Connected!")
        print("My IP address:", wlan.ifconfig()[0])
        return True
    else:
        print("Already connected")
        return True

try:
    if connect_wifi():
        led.value(1)
        print("LED is ON.")
    else:
        print("WiFi connection failed. Blue LED will remain OFF.")
        led.value(0)

except Exception as e:
    print(f"An error occurred: {e}")
    led.value(0)
    print("LED is OFF.")
