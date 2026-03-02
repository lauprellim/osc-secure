'''
sha256-demo.py

'''

import hashlib

msg = b"/note 60 90"
digest = hashlib.sha256(msg).digest()
hexdigest = hashlib.sha256(msg).hexdigest()

print("Message: ", msg)
print("SHA-256 (bytes): ", digest)
print("SHA-256 (hex)  : ", hexdigest)

# show avalanche effect: change a byte
msg2 = b"/note 61 90"
print("\nMessage2: ", msg2)
print("SHA-256 (hex)  : ", hashlib.sha256(msg2).hexdigest())


# need to append BINARY data (b)
# append data to end of message to obtain a new hash
msg3 = f"{msg} extra"
print("\nAppended message: ", msg3)
