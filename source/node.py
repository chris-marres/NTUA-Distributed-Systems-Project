from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain
import glob_variables
import itertools

from threading import Lock, Thread
from collections import deque
from copy import deepcopy
from Crypto.PublicKey import RSA

import requests
import json
import pickle
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


from glob_variables import participants

from pydantic import BaseModel
class TransactionPacket(BaseModel):
	sender_address: str
	receiver_address: str
	amount: int
	rand: str
	transaction_id: str
	transaction_inputs: str
	transaction_outputs: str
	signature: str


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
		self.filter_lock = Lock()
		self.chain_lock = Lock()
		self.block_lock = Lock()
		self.stop_mining = False 
	
	def create_new_block(self):
		# the genesis block is being created
		if len(self.chain.blocks) == 0:
			self.current_block = Block(0, 1)
		else: 
			self.current_block = Block(None, None) 	

	def register_node_to_ring(self, id, ip, port, public_key, balance):
		self.pub_key_str = public_key['n']
		self.ring[self.pub_key_str] = {"id": id, "ip": ip, "port": port, "public_key": public_key, "balance": balance}

	def create_transaction(self, receiver, amount):
		print('Creating transaction')
		# check if this node has enough money to spend
		trans_input = []
		nbcs = 0      

		for trans in self.wallet.transactions: 		
			for output in trans.transaction_outputs:
				if (output['receiver']['n'] == self.wallet.address['n'] and output['unspent']):
					nbcs += output['amount']
					output['unspent'] = False
					trans_input.append(output['transaction_id'])
			if nbcs >= amount:
				break
	
		if nbcs < amount: 
			for trans in self.wallet.transactions:
				for output in trans.transaction_outputs:
					output['unspent'] = True
				print('The sender node does not have enough money to spend for this transaction :/')	
				return False
		
		trans = Transaction(self.wallet.address, receiver, amount, trans_input, nbcs)
		print('Transaction created')
		trans.sign_transaction(self.wallet.private_key)
		print('Transaction signed')
	
		# If broadcasting fails
		print('Broadcasting transaction')
		if not self.broadcast_transaction(trans):
			for trans in self.wallet.transactions:
				for output in trans.transaction_outputs:
					if output['transaction_id'] in trans_input:
						output['unspent'] = True
			return False

		print('Transaction broadcasted')
		return True
	
	def add_init_transaction(self):
		trans = Transaction("0", self.wallet.address, participants * 100, [])
		
		# add the transaction to the list of transactions of the bootstrap node
		self.wallet.transactions.append(trans)
		
		self.ring[self.pub_key_str]['balance'] += participants * 100

		self.current_block.add_transaction(trans)

		return True
	
	def broadcast_transaction(self, transaction):
		print('Sending transaction:')
		for node in self.ring.values():
			if node['id'] != self.id:		
				sender_address_dict = transaction.sender_address

				# Convert dictionary to JSON string
				sender_address_json = json.dumps(sender_address_dict)

				rec_address_dict = {
					'n': transaction.receiver_address.n,
					'e': transaction.receiver_address.e
				}

				# Convert dictionary to JSON string
				rec_address_json = json.dumps(rec_address_dict)

				obj = {
					"sender_address": sender_address_json,
					"receiver_address": rec_address_json,
					"amount": transaction.amount,
					"transaction_id": transaction.transaction_id,
					"transaction_inputs": [item.hexdigest() for item in transaction.transaction_inputs],
					"transaction_outputs": transaction.transaction_outputs,
					"signature": transaction.signature
				}

				obj = json.dumps(obj)
				message = {'transaction_json': obj}
				
				response = requests.post('http://' + node['ip'] + ':' + str(node['port']) + '/receive_transaction', json=message)
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
		self.current_block = self.create_new_block()
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

	def validate_block(self, block):
		return (block.previous_hash == self.chain.blocks[-1].current_hash and (block.current_hash == block.get_hash()))
	"""	if not block.current_hash == block.get_hash():
			print('The current hash of this block is not correct')
			return False
		if new_block:
			if not block.previousHash == self.chain.blocks[-1].current_hash:
				print ('The previous block hash is differnet. There should be a conflict')
				return False
			return True	
		else: 
			pass
	"""


	#consensus functions

	def filter_blocks(self, mined_block):
		with self.block_lock:
			total_transactions = list(itertools.chain.from_iterable(
                [
                    unc_block.transactions
                    for unc_block
                    in self.unconfirmed_blocks
                ]))
			if (self.current_block):
				total_transactions.extend(self.current_block.transactions)
			self.current_block.transactions = []
			filtered_transactions = [
                transaction
                for transaction
                in total_transactions
                if (
                    transaction
                    not in mined_block.transactions
                )
            ]
			final_idx = 0
			if not self.unconfirmed_blocks:
				self.current_block.transactions = deepcopy(filtered_transactions)
				return
			i = 0
			while ((i + 1) * glob_variables.capacity <= len(filtered_transactions)):
				self.unconfirmed_blocks[i].transactions = deepcopy(
					filtered_transactions[i * glob_variables.capacity:(
                        i + 1) * glob_variables.capacity])
				i += 1
			if i * glob_variables.capacity < len(filtered_transactions):
				self.current_block.transactions = deepcopy(
                    filtered_transactions[i * glob_variables.capacity:])
			
			for i in range(len(self.unconfirmed_blocks) - i):
				self.unconfirmed_blocks.pop()
		return

	def validate_chain(self, chain):
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


	def broadcast_ring(self):
		for node in self.ring.values():
			if node['id'] != self.id:

				obj = json.dumps(self.ring)
				message = {'ring_json': obj}

				response = requests.post('http://' + node['ip'] + ':' + str(node['port']) + '/receive_ring', json=message)
				if response.status_code != 200:
					return False
		return True
	

	def resolve_conflicts(self, new_block):
		pass