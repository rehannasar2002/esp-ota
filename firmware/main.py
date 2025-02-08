import machine
import network

led = machine.Pin(2, machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)

print(wlan.ifconfig())
