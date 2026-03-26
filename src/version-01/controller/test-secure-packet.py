'''
test_secure_packet.py
---------------------
Local test for osc_min.py and secure_packet.py.

Builds one OSC message, wraps it in the secure packet format,
and prints the results for inspection.
'''

from osc_min import osc_pack
from secure_packet import build_packet, HEADER_SIZE, TAG_SIZE

# Test values
HMAC_KEY = b'replace-this-with-a-better-random-key'
DEVICE_ID = 1
SEQ = 42

# Build one OSC payload
payload = osc_pack('/controller/pot1', ',f', (0.314,))

# Build secure packet
packet = build_packet(HMAC_KEY, DEVICE_ID, SEQ, payload)

# Slice packet into pieces
header = packet[:HEADER_SIZE]
osc_payload = packet[HEADER_SIZE:-TAG_SIZE]
tag = packet[-TAG_SIZE:]

print('HEADER_SIZE =', HEADER_SIZE)
print('TAG_SIZE    =', TAG_SIZE)
print('')

print('Payload length =', len(payload))
print('Packet length  =', len(packet))
print('Expected total =', HEADER_SIZE + len(payload) + TAG_SIZE)
print('')

print('Header bytes:')
print(header)
print('Header hex:')
print(header.hex())
print('')

print('OSC payload bytes:')
print(osc_payload)
print('OSC payload hex:')
print(osc_payload.hex())
print('')

print('HMAC tag bytes:')
print(tag)
print('HMAC tag hex:')
print(tag.hex())
print('')

print('Full packet hex:')
print(packet.hex())
