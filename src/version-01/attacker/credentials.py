'''
credentials.py
--------------
Local configuration for the ATTACKER Pico W.
'''

WIFI_SSID = 'soundlab-2.4g'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'

DEST_IP = '192.168.1.4'
DEST_PORT = 9000

# Deliberately wrong key for HMAC test
HMAC_KEY = b'wrong-key-on-purpose'

DEVICE_ID = 2

LED_GPIO = 17
BUTTON_GPIO = 16
