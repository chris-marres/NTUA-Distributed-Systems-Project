import glob_variables
import time
import json

from wallet import Wallet
from transaction import Transaction
from Crypto.Hash import SHA256

class Block:

	"""
	A block in the blockchain.
    Each block contains the attributes below:
        id: the sequence number (int) of the block.
        timestamp: timestamp (float) of the creation of the block.
        listOfTransactions: list of all the transactions in the block.
        nonce: the solution (int) of proof-of-work.
		hash: hash of the block.
        previousHash: hash of the previous block in the blockchain.
    """
	# Create block
	def __init__(self, id, prevHash):
		self.id = id
		self.timestamp = time.time()
		self.listOfTransactions = []
		self.nonce = None
		self.hash = None
		self.previousHash = prevHash

	def create_genesis_block(self, bootstrap_address):
		block = Block(0, 1)
		self.nonce = 0
		trans = Transaction(0, bootstrap_address, 100*glob_variables.participants, [])
		self.listOfTransactions.append(trans)
		self.hash = self.get_hash()	
		
	# Calculate the hash of the current block (self.hash)
	def get_hash(self):
		msg = (str([self.timestamp, self.previousHash, [trans['trans_id'] for trans in self.listOfTransactions], self.nonce])).encode()
		hash = SHA256.new(msg)
		return hash
		
	# Override the default method for comparing Block objects	
	def __eq__(self, other):	
		# Two blocks are equal if their hashes are equal
		return self.hash == other.current_hash


	# Add a transaction to the block
	def add_transaction(self, transaction):
		length = len(self.listOfTransactions)
		
		# After the addition of that transaction, the block will be full
		if length == (glob_variables.capacity - 1):
			self.listOfTransactions.append({'sender': transaction.sender_address, 'receiver': transaction.receiver_address, 'amount': transaction.amount, 'signature': transaction.signature})

			return True
		
		# The block is already full
		elif length == glob_variables.capacity:
			print('The block is already full and no more transactions could be added')
		
		# The block is either not full yet or already full -before adding the given transaction-
		return False
	