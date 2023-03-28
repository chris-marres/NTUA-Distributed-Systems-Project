
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
import binascii

# Generate 1024-bit RSA key pair (private + public key)
private_key = RSA.generate(bits=1024)
print(private_key)
print('the type of the private key is', private_key)
pubKey = private_key.publickey()
print('the type of the private key is', pubKey)

# Sign the message using the PKCS#1 v1.5 signature scheme (RSASP1)
msg1 = b'Message for RSA signing'
hash1 = SHA256.new(msg1)
signer = PKCS115_SigScheme(private_key)
signature = signer.sign(hash1)
#print('the type of signature is', signature)
print("Signature:", binascii.hexlify(signature))

# Verify valid PKCS#1 v1.5 signature (RSAVP1)
msg2 = b'Message for RSA signing'
hash2 = SHA256.new(msg2)
#print('the type of hash is', hash)
verifier = PKCS115_SigScheme(pubKey)
try:
    verifier.verify(hash2, signature)
    print("Signature  should be valid.")
except:
    print("Signature is invalid.")

# Verify invalid PKCS#1 v1.5 signature (RSAVP1)
msg3 = b'A tampered message'
hash3 = SHA256.new(msg3)
verifier = PKCS115_SigScheme(pubKey)
try:
    verifier.verify(hash3, signature)
    print("Signature is valid.")
except:
    print("Signature should be invalid.")