'''
attack2.py
---------------------
Attacker Pico W that sends well-formed secure packets,
but with the wrong HMAC key!

Expected result:
- gateway rejects packets with bad_hmac
- Max/MSP receives nothing
'''

import time
import socket
import network
from machine import Pin

from osc_min import osc_pack
from secure_packet import build_packet
from credentials import (
    WIFI_SSID,
    WIFI_PASSWORD,
    DEST_IP,
    DEST_PORT,
    HMAC_KEY,
    DEVICE_ID,
    LED_GPIO,
    BUTTON_GPIO
)

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

def send_bad_secure_osc(sock, dest, seq, address, typetags, args):
    payload = osc_pack(address, typetags, args)
    packet = build_packet(HMAC_KEY, DEVICE_ID, seq, payload)
    sock.sendto(packet, dest)
    return seq + 1

def main():
    wifi_connect()

    led = Pin(LED_GPIO, Pin.OUT)
    led.value(0)

    button = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (DEST_IP, DEST_PORT)

    attack_on = False
    last_button = button.value()
    seq = 1
    fake_button_state = 0

    print('Wrong-key attacker ready. Press button to toggle attack.')
    print('Sending forged secure packets to %s:%d' % dest)

    while True:
        current_button = button.value()

        if last_button == 1 and current_button == 0:
            attack_on = not attack_on
            led.value(1 if attack_on else 0)
            print('attack_on = %s' % attack_on)
            time.sleep_ms(250)

        last_button = current_button

        if attack_on:
            seq = send_bad_secure_osc(
                sock,
                dest,
                seq,
                '/controller/pot1',
                ',f',
                (0.95,)
            )
            print('sent forged secure packet: /controller/pot1 0.95  seq=%d' % (seq - 1))

            fake_button_state = 1 - fake_button_state
            seq = send_bad_secure_osc(
                sock,
                dest,
                seq,
                '/controller/button1',
                ',i',
                (fake_button_state,)
            )
            print('sent forged secure packet: /controller/button1 %d  seq=%d' %
                  (fake_button_state, seq - 1))

            time.sleep_ms(ATTACK_DELAY_MS)
        else:
            time.sleep_ms(20)

main()
