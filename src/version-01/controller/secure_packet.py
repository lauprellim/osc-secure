'''
secure_packet.py
----------------
Build secure UDP datagrams of the form:

[12-byte header][OSC payload][16-byte HMAC tag]

Header format:
- version:     1 byte
- flags:       1 byte
- device_id:   4 bytes
- seq:         4 bytes
- payload_len: 2 bytes

All integer fields are big-endian.
'''

import struct
import hmac
import hashlib

VERSION = 1
FLAGS = 0
HEADER_FORMAT = '>BBIIH'
HEADER_SIZE = 12
TAG_SIZE = 16

def build_header(device_id, seq, payload_len, version=VERSION, flags=FLAGS):
    '''
    Return a 12-byte header.
    '''
    return struct.pack(HEADER_FORMAT, version, flags, device_id, seq, payload_len)

def compute_tag(key, header_bytes, payload_bytes):
    '''
    Compute full HMAC-SHA256 and truncate to 16 bytes.
    '''
    mac = hmac.new(key, header_bytes + payload_bytes, hashlib.sha256).digest()
    return mac[:TAG_SIZE]

def build_packet(key, device_id, seq, payload_bytes):
    '''
    Return the full secure packet:
    [header][payload][tag]
    '''
    payload_len = len(payload_bytes)
    header = build_header(device_id, seq, payload_len)
    tag = compute_tag(key, header, payload_bytes)
    return header + payload_bytes + tag
