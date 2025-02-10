import machine
import network
import time

led = machine.Pin(2, machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)

print(wlan.ifconfig())

def blink_led():
    while True:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)

blink_led()
