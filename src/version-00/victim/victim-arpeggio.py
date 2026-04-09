'''
victim-arpeggio.py
------------------
Rename this main.py on the board.

Victim Pico W demo:

- Button toggles sending on/off (debounced)
- Blue LED indicates "sending"
- Sends a C-major arpeggio (3 octaves, up then down)
- OSC: /note (midi_note, velocity) over UDP to laptop

Wiring:
- Button between GPIO15 and GND (internal pull-up)
- LED anode -> GPIO16 through resistor, cathode -> GND

Files needed:
- osc_min.py
- credentials.py
'''

import time
import network
import socket
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

def build_major_arpeggio(root_midi):
    # Major triad intervals: root, major third, perfect fifth
    intervals = [0, 4, 7]
    notes_up = []

    # 3 octaves of triad tones
    for octv in range(0, 3):
        for iv in intervals:
            notes_up.append(root_midi + 12*octv + iv)

    # Add top root for clear turnaround (optional but musical)
    notes_up.append(root_midi + 36)

    # Mirror down without repeating endpoints
    notes_down = list(reversed(notes_up[1:-1]))
    return notes_up + notes_down

def main():
    cfg = wifi_connect()
    print('Victim WiFi connected:', cfg)
    print('Sending to %s:%d' % (DEST_IP, DEST_PORT))

    btn = Pin(BTN_GPIO, Pin.IN, Pin.PULL_UP)
    led = Pin(LED_GPIO, Pin.OUT)
    led.value(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    seq = build_major_arpeggio(48)  # C3 (C major)
    idx = 0

    sending = False
    last_btn = 1
    last_toggle_ms = time.ticks_ms()

    next_send_ms = time.ticks_ms()

    while True:
        # Debounced toggle on falling edge
        cur = btn.value()
        if last_btn == 1 and cur == 0:
            now = time.ticks_ms()
            if time.ticks_diff(now, last_toggle_ms) > 250:
                sending = not sending
                led.value(1 if sending else 0)
                last_toggle_ms = now
                print('Victim sending=%s' % sending)
        last_btn = cur

        if sending:
            now = time.ticks_ms()
            if time.ticks_diff(now, next_send_ms) >= 0:
                note = seq[idx]
                pkt = osc_pack('/note', ',ii', (note, VEL))
                s.sendto(pkt, (DEST_IP, DEST_PORT))

                idx = (idx + 1) % len(seq)
                next_send_ms = time.ticks_add(now, NOTE_MS)
        else:
            # Keep loop responsive but not busy
            time.sleep_ms(10)

main()
