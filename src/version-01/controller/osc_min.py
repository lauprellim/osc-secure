'''
osc_min.py
----------
Minimal OSC message builder.

Supports:
- int32 (i)
- float32 (f)
'''

import struct

def pad_string(s):
    '''
    OSC strings must be null-terminated and padded to 4 bytes.
    '''
    b = s.encode('utf-8') + b'\x00'
    while len(b) % 4 != 0:
        b += b'\x00'
    return b

def osc_pack(address, typetags, args):
    '''
    Build an OSC message.

    address: string, e.g. "/controller/pot1"
    typetags: string, e.g. ",f" or ",ii"
    args: tuple of values
    '''
    msg = b''

    # Address
    msg += pad_string(address)

    # Type tags
    msg += pad_string(typetags)

    # Arguments
    for t, arg in zip(typetags[1:], args):  # skip leading comma
        if t == 'i':
            msg += struct.pack('>i', arg)
        elif t == 'f':
            msg += struct.pack('>f', arg)
        else:
            raise ValueError('Unsupported OSC type: %s' % t)

    return msg
