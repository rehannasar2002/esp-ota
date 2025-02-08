import network
import ujson
import socket
from machine import Pin
import time
import machine

CONFIG_FILE = "wifi.json"

# LED Indicator (optional)
led = Pin(2, Pin.OUT)  # Adjust for your board


# Load Wi-Fi credentials from JSON file
def load_credentials():
    try:
        with open(CONFIG_FILE, "r") as f:
            return ujson.load(f)
    except Exception as e:
        print("Error loading credentials:", e)
        return None


# Save Wi-Fi credentials to JSON file
def save_credentials(ssid, password):
    try:
        with open(CONFIG_FILE, "w") as f:
            ujson.dump({"ssid": ssid, "password": password}, f)
    except Exception as e:
        print("Error saving credentials:", e)


# Connect to Wi-Fi network
def connect_to_wifi():
    credentials = load_credentials()
    if not credentials:
        print("No credentials found.")
        return False

    ssid = credentials.get("ssid")
    password = credentials.get("password")

    if not ssid or not password:
        print("Invalid credentials.")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Connecting to Wi-Fi...")
    for _ in range(10):  # Retry for 10 seconds
        if wlan.isconnected():
            print("Connected to Wi-Fi:", wlan.ifconfig())
            led.off()  # Turn off LED when connected
            return True
        led.on()
        time.sleep(1)

    print("Failed to connect to Wi-Fi.")
    return False


# Start Wi-Fi access point
def start_access_point():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(
        essid="ESP_Setup", password="12345678", authmode=network.AUTH_WPA_WPA2_PSK
    )
    ap.ifconfig(("192.168.0.1", "255.255.255.0", "192.168.0.1", "8.8.8.8"))
    print("Access Point Started. Connect to 'ESP_Setup' with password '12345678'.")
    print("IP:", ap.ifconfig()[0])
    return ap


# Start a simple web server to capture Wi-Fi credentials
def start_web_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Web server running...")

    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        request = cl.recv(1024).decode()

        if "POST" in request:
            data = request.split("\r\n")[-1]
            params = {k: v for k, v in [x.split("=") for x in data.split("&")]}
            ssid = params.get("ssid")
            password = params.get("password")
            if ssid and password:
                save_credentials(ssid, password)
                response = "<html><body><h3>Credentials Saved!</h3><p>Rebooting device, please reconnect.</p></body></html>"
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + response)
                cl.close()
                time.sleep(2)
                machine.reset()
        else:
            # Captive portal redirect page
            html = """
            <html>
                <head>
                    <title>Wi-Fi Setup</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; background-color: #f9f9f9; padding-top: 50px; }
                        form { display: inline-block; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 15px rgba(0,0,0,0.1); }
                        input { margin: 10px 0; padding: 8px; width: 250px; }
                        button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                        button:hover { background-color: #45a049; }
                    </style>
                </head>
                <body>
                    <h2>Wi-Fi Configuration</h2>
                    <p>Please enter your Wi-Fi details below:</p>
                    <form method="POST">
                        <input type="text" name="ssid" placeholder="Wi-Fi SSID" required><br>
                        <input type="password" name="password" placeholder="Wi-Fi Password" required><br>
                        <button type="submit">Save and Connect</button>
                    </form>
                </body>
            </html>
            """
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html)
            cl.close()


# Main logic
ap = None
if not connect_to_wifi():
    ap = start_access_point()
    start_web_server()
else:
    if ap and ap.active():
        ap.active(False)
    print("Device operational.")

from ota import OTAUpdater

firmware_url = "https://raw.githubusercontent.com/ujjwalshiva/esp-ota/"

ota_updater = OTAUpdater(firmware_url, "main.py")
ota_updater.download_and_install_update_if_available()
