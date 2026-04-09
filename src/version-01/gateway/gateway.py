'''
gateway.py
----------
Receive secure UDP packets from the Pico controller, verify them,
and forward only valid OSC payloads to Max/MSP on localhost.

Secure packet format:
[12-byte header][OSC payload][16-byte HMAC tag]

Header:
- version:     1 byte
- flags:       1 byte
- device_id:   4 bytes
- seq:         4 bytes
- payload_len: 2 bytes
'''

import socket
import struct
import hmac
import hashlib

# WiFi-facing UDP port
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 9000

# Local OSC destination for Max/MSP
FORWARD_HOST = '127.0.0.1'
FORWARD_PORT = 8000

# Must match Pico-side key exactly
HMAC_KEY = b'placeholder-key'

HEADER_FORMAT = '>BBIIH'
HEADER_SIZE = 12
TAG_SIZE = 16

# Track most recent accepted sequence number per device
last_seq_by_device = {}

def parse_header(header_bytes):
    return struct.unpack(HEADER_FORMAT, header_bytes)

def compute_tag(key, header_bytes, payload_bytes):
    mac = hmac.new(key, header_bytes + payload_bytes, hashlib.sha256).digest()
    return mac[:TAG_SIZE]

def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((LISTEN_HOST, LISTEN_PORT))

    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('Gateway is listening on %s:%d' % (LISTEN_HOST, LISTEN_PORT))
    print('Forwarding verified OSC to %s:%d' % (FORWARD_HOST, FORWARD_PORT))
    print('')

    accepted = 0
    bad_hmac = 0
    bad_length = 0
    bad_version = 0
    replay = 0

    while True:
        data, addr = recv_sock.recvfrom(4096)

        if len(data) < HEADER_SIZE + TAG_SIZE:
            bad_length += 1
            print('DROP bad_length: too short from %s:%d len=%d' %
                  (addr[0], addr[1], len(data)))
            continue

        header = data[:HEADER_SIZE]
        version, flags, device_id, seq, payload_len = parse_header(header)

        expected_len = HEADER_SIZE + payload_len + TAG_SIZE
        if len(data) != expected_len:
            bad_length += 1
            print('DROP bad_length: from %s:%d len=%d expected=%d' %
                  (addr[0], addr[1], len(data), expected_len))
            continue

        if version != 1:
            bad_version += 1
            print('DROP bad_version: device=%d seq=%d version=%d' %
                  (device_id, seq, version))
            continue

        payload = data[HEADER_SIZE:HEADER_SIZE + payload_len]
        received_tag = data[-TAG_SIZE:]
        expected_tag = compute_tag(HMAC_KEY, header, payload)

        if not hmac.compare_digest(received_tag, expected_tag):
            bad_hmac += 1
            print('DROP bad_hmac: device=%d seq=%d from %s:%d' %
                  (device_id, seq, addr[0], addr[1]))
            continue

        last_seq = last_seq_by_device.get(device_id, 0)
        if seq <= last_seq:
            replay += 1
            print('DROP replay: device=%d seq=%d last_seq=%d' %
                  (device_id, seq, last_seq))
            continue

        last_seq_by_device[device_id] = seq

        # Forward only the raw OSC payload to Max/MSP
        forward_sock.sendto(payload, (FORWARD_HOST, FORWARD_PORT))

        accepted += 1
        print('ACCEPT device=%d seq=%d payload_len=%d total=%d'
              '  stats: ok=%d hmac=%d replay=%d len=%d bad_version_count=%d' %
              (device_id, seq, payload_len, len(data),
               accepted, bad_hmac, replay, bad_length, bad_version))

if __name__ == '__main__':
    main()
