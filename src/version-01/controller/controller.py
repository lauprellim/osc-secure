'''
controller.py
-------------
Pico W secure OSC controller.

Hardware:
- 1 LED
- 2 buttons (to ground, with internal pull-ups)
- 1 potentiometer on ADC0

Behavior:
- Sends potentiometer changes as OSC float messages
- Sends button press/release changes as OSC integer messages
- Wraps OSC payload in secure packet format
- Sends UDP datagrams to the laptop gateway
'''

import time
import socket
import network
from machine import Pin, ADC

from credentials import (
    WIFI_SSID,
    WIFI_PASSWORD,
    DEST_IP,
    DEST_PORT,
    HMAC_KEY,
    DEVICE_ID,
    LED_GPIO,
    BUTTON1_GPIO,
    BUTTON2_GPIO,
    POT_ADC_GPIO
)

from osc_min import osc_pack
from secure_packet import build_packet

POT_THRESHOLD = 0.02
LOOP_DELAY_MS = 20

def wifi_connect():
    '''
    Connect the Pico W to WiFi.
    '''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to WiFi: %s' % WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(0.2)

    print('WiFi connected.')
    print('Pico IP: %s' % wlan.ifconfig()[0])
    return wlan

def normalize_adc(raw_value):
    '''
    Convert 16-bit ADC reading to float in range 0.0 - 1.0.
    '''
    return raw_value / 65535.0

def send_secure_osc(sock, dest, seq, address, typetags, args):
    '''
    Build OSC payload, wrap securely, send via UDP.
    Returns updated sequence number.
    '''
    payload = osc_pack(address, typetags, args)
    packet = build_packet(HMAC_KEY, DEVICE_ID, seq, payload)
    sock.sendto(packet, dest)
    return seq + 1

def main():
    wifi_connect()

    led = Pin(LED_GPIO, Pin.OUT)
    led.value(1)

    button1 = Pin(BUTTON1_GPIO, Pin.IN, Pin.PULL_UP)
    button2 = Pin(BUTTON2_GPIO, Pin.IN, Pin.PULL_UP)
    pot = ADC(Pin(POT_ADC_GPIO))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (DEST_IP, DEST_PORT)

    seq = 1

    last_button1 = button1.value()
    last_button2 = button2.value()
    last_pot = normalize_adc(pot.read_u16())

    print('Sending to %s:%d' % dest)
    print('Controller ready.')

    while True:
        # Read potentiometer
        current_pot = normalize_adc(pot.read_u16())

        # Only send if change exceeds threshold
        if abs(current_pot - last_pot) >= POT_THRESHOLD:
            seq = send_secure_osc(
                sock,
                dest,
                seq,
                '/controller/pot1',
                ',f',
                (current_pot,)
            )
            print('pot1 = %.3f  seq=%d' % (current_pot, seq - 1))
            last_pot = current_pot

        # Read buttons
        current_button1 = button1.value()
        current_button2 = button2.value()

        # Send only on state change
        if current_button1 != last_button1:
            value = 1 if current_button1 == 0 else 0
            seq = send_secure_osc(
                sock,
                dest,
                seq,
                '/controller/button1',
                ',i',
                (value,)
            )
            print('button1 = %d  seq=%d' % (value, seq - 1))
            last_button1 = current_button1

        if current_button2 != last_button2:
            value = 1 if current_button2 == 0 else 0
            seq = send_secure_osc(
                sock,
                dest,
                seq,
                '/controller/button2',
                ',i',
                (value,)
            )
            print('button2 = %d  seq=%d' % (value, seq - 1))
            last_button2 = current_button2

        time.sleep_ms(LOOP_DELAY_MS)

main()
