'''
controller-latency.py
---------------------
Latency test sender for Pico W
This is part of version-02

Press button 1 to send one secure ping packet.
The gateway will verify and send an ACK back.
This script measures round-trip time and estimates one-way latency.
'''

import time
import socket
import struct
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
    BUTTON1_GPIO
)

ACK_PORT = 9001
LOOP_DELAY_MS = 10

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to WiFi:', WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout_s = 15
        start = time.time()
        while not wlan.isconnected():
            print('WiFi status =', wlan.status())
            time.sleep(1)
            if time.time() - start > timeout_s:
                raise RuntimeError('WiFi connection timed out, status=%s' % wlan.status())

    print('WiFi connected.')
    print('Pico IP =', wlan.ifconfig()[0])
    return wlan

def main():
    wifi_connect()

    led = Pin(LED_GPIO, Pin.OUT)
    led.value(1)

    button = Pin(BUTTON1_GPIO, Pin.IN, Pin.PULL_UP)

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_sock.bind(('0.0.0.0', ACK_PORT))
    ack_sock.settimeout(0)

    dest = (DEST_IP, DEST_PORT)

    seq = 1
    last_button = button.value()

    pending = {}
    rtt_samples_us = []

    print('Latency controller ready.')
    print('Send to %s:%d, listen for ACK on port %d' % (DEST_IP, DEST_PORT, ACK_PORT))

    try:
        while True:
            # Check for ACKs
            try:
                data, addr = ack_sock.recvfrom(16)
                if len(data) == 4:
                    ack_seq = struct.unpack('>I', data)[0]
                    if ack_seq in pending:
                        sent_us = pending.pop(ack_seq)
                        now_us = time.ticks_us()
                        rtt_us = time.ticks_diff(now_us, sent_us)
                        one_way_us = rtt_us / 2.0
                        rtt_samples_us.append(rtt_us)

                        print('ACK seq=%d  RTT=%d us  estimated one-way=%.1f us' %
                              (ack_seq, rtt_us, one_way_us))

                        if len(rtt_samples_us) % 10 == 0:
                            avg = sum(rtt_samples_us) / len(rtt_samples_us)
                            print('RTT stats over %d samples: avg=%.1f us  min=%d us  max=%d us' %
                                  (len(rtt_samples_us), avg,
                                   min(rtt_samples_us), max(rtt_samples_us)))
            except OSError:
                pass

            # Send one ping on button press
            current_button = button.value()
            if last_button == 1 and current_button == 0:
                payload = osc_pack('/latency/ping', ',i', (seq,))
                packet = build_packet(HMAC_KEY, DEVICE_ID, seq, payload)

                pending[seq] = time.ticks_us()
                send_sock.sendto(packet, dest)
                print('Sent seq=%d' % seq)
                seq += 1

                # simple debounce
                time.sleep_ms(200)

            last_button = current_button
            time.sleep_ms(LOOP_DELAY_MS)

    finally:
        print('Stopping latency controller.')
        led.value(0)

main()
