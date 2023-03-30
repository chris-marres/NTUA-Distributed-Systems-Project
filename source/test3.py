from Crypto.PublicKey import RSA

keyPair = RSA.generate(bits=1024)
print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")
privateKey = keyPair.exportKey()
publicKey = {'n': keyPair.n, 'e': keyPair.e}

msg = b'Hello'

from hashlib import sha512

hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
signature = pow(hash, keyPair.d, keyPair.n)
print("Signature:", hex(signature))

hashFromSignature = pow(signature, publicKey['e'], publicKey['n'])
print("Signature valid:", hash == hashFromSignature)