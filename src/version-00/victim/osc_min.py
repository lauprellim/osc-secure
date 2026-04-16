'''
osc_min.py
----------
Simple OSC encoder for MicroPython

Functionality:
- creates a valid OSC address string
- type tag string
- int32 arguments (OSC "i")

The caller of this function will send
the bytes that are returned over UDP.
'''

import struct

def _pad4(b):
    # Pad with NULs so len is a multiple of 4
    n = (4 - (len(b) % 4)) % 4
    return b + (b'\x00' * n)

def osc_pack(address, typetags, args):
    ab = _pad4(address.encode('utf-8') + b'\x00')
    tb = _pad4(typetags.encode('utf-8') + b'\x00')

    data = b''
    for t, a in zip(typetags[1:], args):
        if t != 'i':
            raise ValueError('Unsupported OSC type: %s' % t)
        data += struct.pack('>i', int(a))  # needs to be big-endian int32

    return ab + tb + data