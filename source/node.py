from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain
from transaction_Input import TransactionInput
import glob_variables

from threading import Lock, Thread
from collections import deque
from copy import deepcopy
from Crypto.PublicKey import RSA

import requests
import json


from glob_variables import participants

class Node:

	def __init__(self):
		self.id = None
		self.nbc = 0
		self.chain = Blockchain()
		self.wallet = Wallet()
		#Ring: information regarding the id, ip, port, public key and balance of every node
		self.current_block = None
		self.ring = {}
		self.unconfirmed_blocks = deque()
		self.block_lock = Lock() 
	
	def create_new_block(self):
		# the genesis block is being created
		if len(self.chain.blocks) == 0:
			self.current_block = Block(0, 1)
		else: 
			self.current_block = Block(None, None) 	

	def register_node_to_ring(self, id, ip, port, public_key, balance):
		self.pub_key_str = public_key.export_key().decode("utf-8")
		self.ring[self.pub_key_str] = {"id": id, "ip": ip, "port": port, "public_key": public_key, "balance": balance}

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
	
	def add_init_transaction(self):
		trans = Transaction("0", self.wallet.address, participants * 100, [])
		
		# add the transaction to the list of transactions of the bootstrap node
		self.wallet.transactions.append(trans)
		
		self.ring[self.pub_key_str]['balance'] += participants * 100

		self.current_block.add_transaction(trans)

		return True
	
	def broadcast_transaction(self, transaction):
		for node in self.ring.values():
			if node['id'] != self.id:
				obj = json.dumps(transaction.__dict__)
				response = requests.post('http://' + node['ip'] + ':' + str(node['port']) + '/receive_transaction', json=obj)
				if response.status_code != 200:
					return False
		return True

	def validate_transaction(self, trans):
		# check if the signature is valid
		if (not trans.verify_signature()):
			print('The signature is not valid')
			return False
		
		#check if sender has enough money
		if self.ring[self.pub_key_str]['balance'] >= trans.amount:
			#create the 2 transaction outputs and add them in UTXOs list.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			return True
		print('There are not enough money to be spent')		
		return False 

	
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

		
    #----------------------------------------------------------------------------------------------------------------------------

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


  
	#def broadcast_block(self):

	def validate_block(self, block, new_block = True):
		if not block.current_hash == block.get_hash():
			print('The current hash of this block is not correct')
			return False
		if new_block:
			if not block.previousHash == self.chain.blocks[-1].current_hash:
				print ('The previous block hash is differnet. There should be a conflict')
				return False
			return True	
		else: 
			pass


	#consensus functions

	"""	
	def validate_chain(self, chain):
		for block in chain.blocks:






        blocks = chain.blocks
        for i in range(len(blocks)):
            if i == 0:
                if (blocks[i].previous_hash != 1 or
                        blocks[i].current_hash != blocks[i].get_hash()):
                    return False
            else:
                valid_current_hash = (
                    blocks[i].current_hash == blocks[i].get_hash()
                )
                valid_previous_hash = (
                    blocks[i].previous_hash == blocks[i - 1].current_hash
                )
                if not valid_current_hash or not valid_previous_hash:
                    return False
        return True
	"""

	def resolve_conflicts(self):
		#resolve correct chain
		pass
