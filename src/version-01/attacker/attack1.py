'''
attack1.py
-----------
Unauthorized sender transmits plain OSC directly to the
gateway's secure UDP port, without secure header or HMAC.

Expected result:
- gateway should reject packets that aren't formed correctly
- Max/MSP receives NUTHIN

The gateway will reject the packets because there will be a nonsense
payload_len, which is the result of interpreting plain OSC bytes
(with no header, or HMAC) *as if* they were a secure message.

'''

import time
import socket
import network
from machine import Pin
from osc_min import osc_pack
from credentials import WIFI_SSID, WIFI_PASSWORD, DEST_IP, DEST_PORT, LED_GPIO, BUTTON_GPIO

ATTACK_DELAY_MS = 150

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to WiFi: %s' % WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(0.2)

    print('WiFi connected.')
    print('Attacker IP: %s' % wlan.ifconfig()[0])
    return wlan

def main():
    wifi_connect()

    led = Pin(LED_GPIO, Pin.OUT)
    led.value(0)

    button = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (DEST_IP, DEST_PORT)

    attack_on = False
    last_button = button.value()
    fake_button_state = 0

    print('Attacker is ready! Press button to toggle attack on/off. Hahaha!')
    print('Sending plain OSC to %s:%d' % dest)

    while True:
        current_button = button.value()

        # Toggle attack mode on falling edge
        if last_button == 1 and current_button == 0:
            attack_on = not attack_on
            led.value(1 if attack_on else 0)
            print('attack_on = %s' % attack_on)
            time.sleep_ms(250)

        last_button = current_button

        if attack_on:
            # Fake continuous control message
            pot_msg = osc_pack('/controller/pot1', ',f', (0.95,))
            sock.sendto(pot_msg, dest)
            print('sent plain OSC: /controller/pot1 0.95')

            # Fake button message
            fake_button_state = 1 - fake_button_state
            button_msg = osc_pack('/controller/button1', ',i', (fake_button_state,))
            sock.sendto(button_msg, dest)
            print('sent plain OSC: /controller/button1 %d' % fake_button_state)

            time.sleep_ms(ATTACK_DELAY_MS)
        else:
            time.sleep_ms(20)

main()