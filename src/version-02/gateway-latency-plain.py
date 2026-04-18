'''
gateway-latency-plain.py
------------------------
Plain OSC latency test gateway.

Receives plain OSC packets from the Pico controller,
does not verify HMAC, and sends an ACK (the sequence number) back.

Also measures gateway-side processing overhead for the plain case.
'''

import socket
import struct
import time

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 9000

FORWARD_HOST = '127.0.0.1'
FORWARD_PORT = 8000

ACK_PORT = 9001

processing_us = []

def extract_seq_from_plain_ping(payload):
    '''
    Assumes payload is:
    /latency/ping ,i <int32 seq>

    Structure:
    [address padded][typetag padded][4-byte int]
    We know the final 4 bytes are the integer seq.
    '''
    if len(payload) < 4:
        raise ValueError('payload too short')
    return struct.unpack('>i', payload[-4:])[0]

def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((LISTEN_HOST, LISTEN_PORT))

    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('Plain gateway latency test listening on %s:%d' % (LISTEN_HOST, LISTEN_PORT))
    print('Forwarding plain OSC to %s:%d' % (FORWARD_HOST, FORWARD_PORT))
    print('Sending ACKs back on port %d' % ACK_PORT)
    print('')

    accepted = 0
    bad_parse = 0

    while True:
        payload, addr = recv_sock.recvfrom(4096)
        t0 = time.perf_counter_ns()

        try:
            seq = extract_seq_from_plain_ping(payload)
        except Exception as e:
            bad_parse += 1
            print('DROP bad_parse from %s:%d len=%d error=%s' %
                  (addr[0], addr[1], len(payload), e))
            continue

        forward_sock.sendto(payload, (FORWARD_HOST, FORWARD_PORT))

        ack_data = struct.pack('>I', seq)
        ack_sock.sendto(ack_data, (addr[0], ACK_PORT))

        t1 = time.perf_counter_ns()
        delta_us = (t1 - t0) / 1000.0
        processing_us.append(delta_us)

        accepted += 1
        print('ACCEPT seq=%d payload_len=%d gateway_us=%.1f  stats: ok=%d bad_parse=%d' %
              (seq, len(payload), delta_us, accepted, bad_parse))

        if accepted % 10 == 0:
            avg = sum(processing_us) / len(processing_us)
            print('Plain gateway timing over %d accepted packets: avg=%.1f us min=%.1f us max=%.1f us' %
                  (len(processing_us), avg, min(processing_us), max(processing_us)))
            print('')

if __name__ == '__main__':
    main()
