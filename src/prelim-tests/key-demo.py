'''
key-demo.py

Simple demonstration of HMAC-SHA256 authentication and verification.

- computes full HMAC
- truncates to 16 bytes
- appends to some message
- verifies authenticity

System is sending a 16-byte authentication tag derived from the secret key
that is never transmitted...

The HMAC hash is derived FCROM THE PACKET'S INFORMATION ITSELF
AND the SECRET KEY COMBINED.

This is called "unforgeability under chosen-message attack".



'''

import hmac
import hashlib

# config
key = b"password123"             # a stupid password for practice
# key_guess = b"attackerguess"     # attacker guesses this key

message1 = b"header||osc_payload_example"
message2 = b"header||new_payload_example"

HMAC_TRUNCATE_BYTES = 16

# -------------------------------
# sender side

print("=== sender side ===")

# compute full HMAC (32 bytes for SHA256)
full_hmac1 = hmac.new(key, message1, hashlib.sha256).digest()
full_hmac2 = hmac.new(key, message2, hashlib.sha256).digest()

# trucate to 16 bytes
truncated_hmac1 = full_hmac1[:HMAC_TRUNCATE_BYTES]
truncated_hmac2 = full_hmac2[:HMAC_TRUNCATE_BYTES]

# construct transmitted packet
packet1 = message1 + truncated_hmac1
packet2 = message2 + truncated_hmac2

print("\nMessage1: ",  message1)
print("Message2: ",  message2)


print("\nFull HMAC1 (32 bytes): ", full_hmac1.hex())
print("\nFull HMAC2 (32 bytes): ", full_hmac2.hex())


print("\nTruncated HMAC1 (16 bytes): ", truncated_hmac1.hex())
print("\nTruncated HMAC2 (16 bytes): ", truncated_hmac2.hex())



# ----------------------------------
# receiver side

print("\n=== receiver side ===");


print(f"\nPacket1: {packet1}");
print(f"Packet2: {packet2}");

# receiver spliits packet
received_message1 = packet1[:-HMAC_TRUNCATE_BYTES]
received_message2 = packet2[:-HMAC_TRUNCATE_BYTES]

received_tag1 = packet1[-HMAC_TRUNCATE_BYTES:]
received_tag2 = packet2[-HMAC_TRUNCATE_BYTES:]

# recompute HMAC
expected_full_hmac1 = hmac.new(key, received_message1, hashlib.sha256).digest()
expected_truncated1 = expected_full_hmac1[:HMAC_TRUNCATE_BYTES]

expected_full_hmac2 = hmac.new(key, received_message2, hashlib.sha256).digest()
expected_truncated2 = expected_full_hmac2[:HMAC_TRUNCATE_BYTES]

print("\nReceived message1: ", received_message1)
print("Received message2: ", received_message2)


print("\nReceived tag1: ", received_tag1.hex())
print("Expected tag1: ", expected_truncated1.hex())

print("\nReceived tag2: ", received_tag2.hex())
print("Expected tag2: ", expected_truncated2.hex())


# constant time comparison
if (hmac.compare_digest(received_tag1, expected_truncated1)) and (hmac.compare_digest(received_tag2, expected_truncated2)):
    print("\nVerification is successful: message is authentic.");
else:
    print("\nVerifaction failure: message is invalid.")
