'''
credentials.py
--------------
Local configuration for the Pico W controller.

Keep this file out of public repositories if it contains real credentials.
'''

WIFI_SSID = 'soundlab-2.4g'
# replace this with real password
WIFI_PASSWORD = '****'

DEST_IP = '192.168.1.4'
DEST_PORT = 9000

# 32-byte key is a good default for HMAC-SHA256.
# This is just a placeholder.
HMAC_KEY = b'placeholder-key'

DEVICE_ID = 1

# GPIO assignments
LED_GPIO = 17
BUTTON1_GPIO = 14
BUTTON2_GPIO = 15
POT_ADC_GPIO = 26   # ADC0 on Pico W
