'''
attack3.py
------------------
Replay previously captured legitimate packets. In this really simple demonstration,
I just copied packets that I received and will replay them. I'm not actaully sniffing
packets on WiFi.

Expected:
- gateway will rejects with DROP replay
- Max receives nothing at all.
'''

import time
import socket
import network
from machine import Pin
from credentials import WIFI_SSID, WIFI_PASSWORD, DEST_IP, DEST_PORT, LED_GPIO, BUTTON_GPIO

REPLAY_PACKETS = [
    # This is a real packet captured using listen-udp.py
    '0100000000010000001a001c2f636f6e74726f6c6c65722f706f7431000000002c6600003e3d08bdd73290274147c6319a1499ae7c2373c9',
]

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.2)

    print('Attacker IP:', wlan.ifconfig()[0])

def main():
    wifi_connect()

    led = Pin(LED_GPIO, Pin.OUT)
    button = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (DEST_IP, DEST_PORT)

    attack_on = False
    last_button = button.value()

    print('Replay attacker ready. Press the button to replay captured packet!')

    while True:
        current_button = button.value()

        if last_button == 1 and current_button == 0:
            attack_on = not attack_on
            led.value(attack_on)
            print('attack_on =', attack_on)
            time.sleep_ms(300)

        last_button = current_button

        if attack_on:
            for pkt_hex in REPLAY_PACKETS:
                pkt = bytes.fromhex(pkt_hex)
                sock.sendto(pkt, dest)
                print('replayed packet')
                time.sleep_ms(200)

        else:
            time.sleep_ms(20)

main()
