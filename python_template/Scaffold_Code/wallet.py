from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

# Generate 1024-bit RSA key pair (private + public key)
private_key = RSA.generate(bits=1024)
print(private_key)
pubKey = private_key.publickey()

import rsa

class Wallet:

	"""
    The wallet of a node in the network.
    Each block contains the attributes below:
        private_key: the private key of the node.
        public_key: the public key of the node.
		address: the public key of the node, which serves as its address as well.
        transactions: list which contains the transactions of the node.
    """	

	def __init__(self):
		self.private_key = RSA.generate(bits=2048)
		self.public_key = private_key.publickey()

		"""with open("public.pem", "wb") as f:
			f.write(self.public_key.save_pkcs1("PEM"))
		
		with open("private.pem", "wb") as f:
			f.write(self.private_key.save_pkcs1("PEM"))"""
		
		self.address = self.public_key
		self.transactions = []
		
	def balance(self):
		total_amount = 0
		for trans in self.transactions:
			for output in trans.transaction_outputs: 
				if output.receiver == self.address and output.unspent:
					total_amount += output.amount
		return total_amount