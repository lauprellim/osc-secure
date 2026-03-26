'''
credentials.py
--------------
Local configuration for the Pico W controller.

Keep this file out of public repositories if it contains real credentials.
'''

WIFI_SSID = 'YOUR_WIFI_NAME'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'

DEST_IP = '192.168.1.100'
DEST_PORT = 9000

# 32-byte key is a good default for HMAC-SHA256.
# This is just a placeholder.
HMAC_KEY = b'replace-this-with-a-better-random-key'

DEVICE_ID = 1

# GPIO assignments
LED_GPIO = 17
BUTTON1_GPIO = 14
BUTTON2_GPIO = 15
SLIDER_ADC_GPIO = 26   # ADC0 on Pico W
