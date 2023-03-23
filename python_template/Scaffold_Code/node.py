from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain
from transaction_Input import TransactionInput


from glob_variables import participants

class node:

	def __init__(self):
		self.id = None
		self.NBC = 0
		self.chain = Blockchain()
		self.wallet = Wallet()
		#Ring: information regarding the id, ip, port, public key and balance of every node
		self.ring = []   
	
	def create_new_block(self, index, prevHash):
		self.block = Block(index, prevHash)

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
					#create the 2 transaction outputs and add them in UTXOs list.
					return True
		print('There are not enough money to be spent')		
		return False 

	def add_transaction_to_block(self):
		if 
		#if enough transactions  mine



	def mine_block(self):



	def broadcast_block(self):


	def valid_proof(self, difficulty=MINING_DIFFICULTY):

	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain
