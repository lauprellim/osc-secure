'''
attacker-random.py
------------------
Attacker Pico W demo (baseline insecurity):

- Button toggles sending on/off (debounced)
- LED indicates "sending"
- Sends RANDOM MIDI notes within the same 3-octave range as the victim
- OSC: /note (midi_note, velocity) over UDP to laptop

Wiring:
- Button between GPIO16 and GND (internal pull-up)
- LED anode -> GPIO17 through ~330 ohm, cathode -> GND

Files needed:
- osc_min.py
- credentials.py
'''

import time
import network
import socket
import urandom
from machine import Pin

from osc_min import osc_pack
from credentials import WIFI_SSID, WIFI_PASS, DEST_IP, DEST_PORT

BTN_GPIO = 16
LED_GPIO = 17

NOTE_MS = 100
VEL     = 90

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.2)
    return wlan.ifconfig()

def victim_range():
    # Victim uses build_major_arpeggio(48) and appends root+36.
    # That yields notes in [48, 84] inclusive.
    # We'll disrupt within the full chromatic range across those octaves.
    return 48, 84

def main():
    cfg = wifi_connect()
    print('Attacker WiFi connected:', cfg)
    print('Sending to %s:%d' % (DEST_IP, DEST_PORT))

    btn = Pin(BTN_GPIO, Pin.IN, Pin.PULL_UP)
    led = Pin(LED_GPIO, Pin.OUT)
    led.value(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    lo, hi = victim_range()

    sending = False
    last_btn = 1
    last_toggle_ms = time.ticks_ms()
    next_send_ms = time.ticks_ms()

    print('Attacker: idle (press button to start)')

    while True:
        # Debounced toggle on falling edge
        cur = btn.value()
        if last_btn == 1 and cur == 0:
            now = time.ticks_ms()
            if time.ticks_diff(now, last_toggle_ms) > 250:
                sending = not sending
                led.value(1 if sending else 0)
                last_toggle_ms = now
                if sending:
                    print('Attacker: TRANSMIT ON')
                else:
                    print('Attacker: transmit off')
        last_btn = cur

        if sending:
            now = time.ticks_ms()
            if time.ticks_diff(now, next_send_ms) >= 0:
                note = lo + (urandom.getrandbits(8) % (hi - lo + 1))
                pkt = osc_pack('/note', ',ii', (note, VEL))
                s.sendto(pkt, (DEST_IP, DEST_PORT))
                next_send_ms = time.ticks_add(now, NOTE_MS)
        else:
            time.sleep_ms(10)

main()