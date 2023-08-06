import pickle

import rsa
from Crypto.PublicKey import RSA

# create SHA-256 hash
msg_to_hash = "hello"
trans_id = rsa.compute_hash(msg_to_hash.encode(), "SHA-256")
serialized_data = pickle.dumps(trans_id)
received = pickle.loads(serialized_data)
print("Initial hash:", trans_id, flush=True)
print("Received hash:", received, flush=True)


# create RSA key pair
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# sign hash with private key
signature = rsa.sign_hash(received, private_key, "SHA-256")
print("Signature:", signature, flush=True)

# verify signature with public key
try:
    rsa.verify(received, signature, public_key)
    print("Signature is valid", flush=True)
except:
    print("Signature is invalid", flush=True)
