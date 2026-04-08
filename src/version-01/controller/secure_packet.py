'''
secure_packet.py
----------------
MicroPython-compatible secure packet builder.
No hmac library so implementing one using hashlib instead!

Builds:
[12-byte header][OSC payload][16-byte HMAC tag]
'''

import struct
import hashlib

VERSION = 1
FLAGS = 0
HEADER_FORMAT = '>BBIIH'
HEADER_SIZE = 12
TAG_SIZE = 16
BLOCK_SIZE = 64  # block size for SHA-256

def build_header(device_id, seq, payload_len, version=VERSION, flags=FLAGS):
    return struct.pack(HEADER_FORMAT, version, flags, device_id, seq, payload_len)

def hmac_sha256(key, message):
    '''
    Minimal HMAC-SHA256 implementation for MicroPython.
    '''
    if len(key) > BLOCK_SIZE:
        key = hashlib.sha256(key).digest()

    if len(key) < BLOCK_SIZE:
        key = key + b'\x00' * (BLOCK_SIZE - len(key))

    o_key_pad = bytes((b ^ 0x5c) for b in key)
    i_key_pad = bytes((b ^ 0x36) for b in key)

    inner = hashlib.sha256(i_key_pad + message).digest()
    outer = hashlib.sha256(o_key_pad + inner).digest()

    return outer

def compute_tag(key, header_bytes, payload_bytes):
    mac = hmac_sha256(key, header_bytes + payload_bytes)
    return mac[:TAG_SIZE]

def build_packet(key, device_id, seq, payload_bytes):
    payload_len = len(payload_bytes)
    header = build_header(device_id, seq, payload_len)
    tag = compute_tag(key, header, payload_bytes)
    return header + payload_bytes + tag
