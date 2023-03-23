from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode
import rsa

def encrypt(message, pub_key):
    #RSA encryption protocol according to PKCS#1 OAEP
    cipher = PKCS1_OAEP.new(pub_key)
    return cipher.encrypt(message)

def decrypt(ciphertext, priv_key):
    #RSA encryption protocol according to PKCS#1 OAEP
    cipher = PKCS1_OAEP.new(priv_key)
    return cipher.decrypt(ciphertext)

def sign(message, priv_key):
    signer = PKCS1_v1_5.new(priv_key)
    digest = SHA256.new()
    digest.update(message)
    return signer.sign(digest)

def verifye(message, signature, pub_key):
    signer = PKCS1_v1_5.new(pub_key)
    digest = SHA256.new()
    digest.update(message)
    return signer.verify(digest, signature)


msg1 = b"Hello Tony, I am Jarvis!"
msg2 = b"Hello Toni, I am Jarvis!"
keysize = 2048
(public, private) = rsa.newkeys(keysize)
encrypted = b64encode(rsa.encrypt(msg2, public))
decrypted = rsa.decrypt(b64decode(encrypted), private)
signature = b64encode(rsa.sign(msg1, private, "SHA-256"))
verify = rsa.verify(msg1, b64decode(signature), public)

#print(private.exportKey('PEM'))
#print(public.exportKey('PEM'))
print("Encrypted: ", encrypted)
print("Decrypted: '%s'" % decrypted)
print("Signature: ", signature)
print("Verify: %s" % verify)
#rsa.verify(msg2, b64decode(signature), public)