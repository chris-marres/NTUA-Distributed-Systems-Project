import hashlib
import time

import glob_variables


class Block:

    """
        A block in the blockchain.
    Each block contains the attributes below:
        id: the sequence number (int) of the block.
        timestamp: timestamp (float) of the creation of the block.
        listOfTransactions: list of all the transactions in the block.
        nonce: the solution (int) of proof-of-work.
                current_hash: the hash of the block.
        previousHash: the hash of the previous block in the blockchain.
    """

    # Create block
    def __init__(self, index, prevHash):
        self.index = index
        self.timestamp = time.time()
        self.listOfTransactions = []
        self.nonce = None
        self.current_hash = None
        self.previous_hash = prevHash

    # Calculate the hash of the current block (self.hash)
    def get_hash(self):
        # need to change that as we changed the transaction
        msg = str(
            [
                self.timestamp,
                self.previous_hash,
                [trans.transaction_id for trans in self.listOfTransactions],
                self.nonce,
            ]
        ).encode()
        hash = hashlib.sha256(msg).hexdigest()
        return hash

    # Override the default method for comparing Block objects
    def __eq__(self, other):
        # Two blocks are equal if their hashes are equal
        return self.current_hash == other.current_hash

    # Add a transaction to the block
    def add_transaction(self, transaction):
        length = len(self.listOfTransactions)

        # After the addition of that transaction, the block will be full
        if length == (glob_variables.capacity - 1):
            self.listOfTransactions.append(transaction)
            return True

        # The block is already full
        elif length == glob_variables.capacity:
            print(
                "The block is already full and no more transactions could be added"
            )

        # The block is either not full yet or already full -before adding the given transaction-
        return False
