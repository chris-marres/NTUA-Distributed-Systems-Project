import binascii

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

# Generate 1024-bit RSA key pair (private + public key)
private_key = RSA.generate(bits=1024)
print(private_key, flush=True)
print("the type of the private key is", private_key, flush=True)
pubKey = private_key.publickey()
print("the type of the private key is", pubKey, flush=True)

# Sign the message using the PKCS#1 v1.5 signature scheme (RSASP1)
msg1 = b"Message for RSA signing"
hash1 = SHA256.new(msg1)
signer = PKCS115_SigScheme(private_key)
signature = signer.sign(hash1)
# print('the type of signature is', signature, flush=True)
print("Signature:", binascii.hexlify(signature), flush=True)

# Verify valid PKCS#1 v1.5 signature (RSAVP1)
msg2 = b"Message for RSA signing"
hash2 = SHA256.new(msg2)
# print('the type of hash is', hash, flush=True)
verifier = PKCS115_SigScheme(pubKey)
try:
    verifier.verify(hash2, signature)
    print("Signature  should be valid.", flush=True)
except:
    print("Signature is invalid.", flush=True)

# Verify invalid PKCS#1 v1.5 signature (RSAVP1)
msg3 = b"A tampered message"
hash3 = SHA256.new(msg3)
verifier = PKCS115_SigScheme(pubKey)
try:
    verifier.verify(hash3, signature)
    print("Signature is valid.", flush=True)
except:
    print("Signature should be invalid.", flush=True)
