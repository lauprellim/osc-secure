'''
gateway-latency.py
------------------
Latency test gateway
This goes on the mac and needs a Pico W with controller-latency.py

Receives secure packets, verifies them, forwards OSC to Max,
and sends an ACK (the sequence number) back to the Pico.
Also measures gateway-side processing overhead.
'''

import socket
import struct
import hmac
import hashlib
import time

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 9000

FORWARD_HOST = '127.0.0.1'
FORWARD_PORT = 8000

ACK_PORT = 9001

HMAC_KEY = b'placeholder-key'

HEADER_FORMAT = '>BBIIH'
HEADER_SIZE = 12
TAG_SIZE = 16

last_seq_by_device = {}
processing_us = []

def parse_header(header_bytes):
    return struct.unpack(HEADER_FORMAT, header_bytes)

def compute_tag(key, header_bytes, payload_bytes):
    mac = hmac.new(key, header_bytes + payload_bytes, hashlib.sha256).digest()
    return mac[:TAG_SIZE]

def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((LISTEN_HOST, LISTEN_PORT))

    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('Gateway latency test listening on %s:%d' % (LISTEN_HOST, LISTEN_PORT))
    print('Forwarding verified OSC to %s:%d' % (FORWARD_HOST, FORWARD_PORT))
    print('Sending ACKs back on port %d' % ACK_PORT)
    print('')

    accepted = 0
    bad_hmac = 0
    bad_length = 0
    bad_version_count = 0
    replay = 0

    while True:
        data, addr = recv_sock.recvfrom(4096)
        t0 = time.perf_counter_ns()

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
            bad_version_count += 1
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

        # Forward OSC to Max
        forward_sock.sendto(payload, (FORWARD_HOST, FORWARD_PORT))

        # ACK back to Pico with just the sequence number
        ack_data = struct.pack('>I', seq)
        ack_sock.sendto(ack_data, (addr[0], ACK_PORT))

        t1 = time.perf_counter_ns()
        delta_us = (t1 - t0) / 1000.0
        processing_us.append(delta_us)

        accepted += 1
        print('ACCEPT device=%d seq=%d payload_len=%d total=%d gateway_us=%.1f'
              '  stats: ok=%d hmac=%d replay=%d len=%d bad_version_count=%d' %
              (device_id, seq, payload_len, len(data), delta_us,
               accepted, bad_hmac, replay, bad_length, bad_version_count))

        if accepted % 10 == 0:
            avg = sum(processing_us) / len(processing_us)
            print('Gateway timing over %d accepted packets: avg=%.1f us min=%.1f us max=%.1f us' %
                  (len(processing_us), avg, min(processing_us), max(processing_us)))
            print('')

if __name__ == '__main__':
    main()
