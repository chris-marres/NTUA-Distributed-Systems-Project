from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain
from transaction_Input import TransactionInput
import glob_variables

from threading import Lock, Thread
from collections import deque
from copy import deepcopy


from glob_variables import participants

class node:

	def __init__(self):
		self.id = None
		self.nbc = 0
		self.chain = Blockchain()
		self.wallet = Wallet()
		#Ring: information regarding the id, ip, port, public key and balance of every node
		self.current_block = None
		self.ring = []  
		self.unconfirmed_blocks = deque()
		self.block_lock = Lock() 
	
	def create_new_block(self):
		# the genesis block is being created
		if len(self.chain.blocks) == 0:
			self.current_block = Block(0, 1)
		else: 
			self.current_block = Block(None, None) 	

	def register_node_to_ring(self, id, ip, port, public_key, balance):
		self.ring.append(
            {
                'id': id,
                'ip': ip,
                'port': port,
                'public_key': public_key,
                'balance': balance
            })

	def create_transaction(self, receiver, amount):
		# check if this node has enough money to spend
		trans_input = []
		nbcs = 0        
		for trans in self.wallet.transactions: 		
			for output in trans.transaction_outputs:
				if (output.receiver == self.wallet.address and output.unspent):
					nbcs += output.amount
					output.unspent = False
					trans_input.append(TransactionInput(output.transaction_id))
				if nbcs >= amount:
					break
		if nbcs < amount: 
			for trans in self.wallet.transactions:
				for output in trans.transaction_outputs:
					output.unspent = True
				return False
		
		trans = Transaction(self.wallet.address, receiver, amount, trans_input)
		trans.sign_transaction(self.wallet.private_key)
	
		# If broadcasting fails
		if not self.broadcast_transaction(trans):
			for trans in self.wallet.transactions:
				for output in trans.transaction_outputs:
					if TransactionInput(output.transaction_id) in trans_input:
						output.unspent = True
			return False

		return True
	
	def broadcast_transaction(self, transaction):
		pass

	def validate_transaction(self, trans):
		# check if the signature is valid
		if (not trans.verify_signature()):
			print('The signature is not valid')
			return False
		
		#check if sender has enough money
		for node in self.ring:
			if node['public_key'] == trans.sender_address:
				if node['balance'] >= trans.amount:
					#create the 2 transaction outputs and add them in UTXOs list.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
					return True
		print('There are not enough money to be spent')		
		return False 

	"""
	def add_transaction_to_block(self, trans):
		# add transaction to the list of transactions of the sender and the receiver node
		if (trans.sender_address == self.wallet.public_key or trans.receiver_address == self.wallet.public_key):
			self.wallet.transactions.append(trans)
		
		# update the balance of the sender and the receiver 
		for ring_node in self.ring:
			if ring_node['public_key'] == trans.sender_address:
				ring_node['balance'] -= trans.amount
			if ring_node['public_key'] == trans.receiver_address:
				ring_node['balance'] += trans.amount

        # If the chain contains only the genesis block, a new block
        # is created. In other cases, the block is created after mining.
		if self.current_block is None:
			self.create_new_block()

		self.block_lock.acquire()
		# if after adding this transaction, block is not yet full
		if not self.current_block.add_transaction(trans):
			self.block_lock.release()
			return
		# if block is now full, start the mining procedure

		# First, add the current block in the queue of unconfirmed blocks
		self.unconfirmed_blocks.append(deepcopy(self.current_block))
		# Mining procedure includes:
		# - 
		# - wait until the thread gets the lock.
		# - check that the queue is not empty.
		# - mine the first block of the queue.
		# - if mining succeeds, broadcast the mined block.
		# - if mining fails, put the block back in the queue and wait
		#   for the lock.

		
    

		# Update previous hash and index in case of insertions in the chain
		
		self.create_new_block()
		self.block_lock.release()
		while True:
			with self.filter_lock:
				if (self.unconfirmed_blocks):
					mined_block = self.unconfirmed_blocks.popleft()
					mining_result = self.mine_block(mined_block)
					if (mining_result):
						break
					else:
						self.unconfirmed_blocks.appendleft(mined_block)
				else:
					return
		self.broadcast_block(mined_block)
        
	def mine_block(self, block):
		block.nonce = 0
		block.index = self.chain.blocks[-1].index + 1
		block.previous_hash = self.chain.blocks[-1].current_hash
		computed_hash = block.get_hash()
		while (not computed_hash.startswith('0' * glob_variables.mining_difficulty) and not self.stop_mining):
			block.nonce += 1
			computed_hash = block.get_hash()
		block.current_hash = computed_hash

		return not self.stop_mining



	def broadcast_block(self):


	def valid_proof(self, difficulty=MINING_DIFFICULTY):

	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain
"""