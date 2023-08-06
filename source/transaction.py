from hashlib import sha256

# import requests
# from flask import Flask, jsonify, request, render_template


class Transaction:

    """
    A noobcash transaction in the blockchain.
    Each transaction contains the attributes below:
        sender_address: the public key of the sender's wallet (wallet1).
        receiver_address: the public key of the receiver's wallet (wallet2).
        amount: the amount (int) of nbc which will be transfered.
        transaction_id: the hash of the transaction.
        transaction_inputs: list of TransactionInput.
        transaction_outputs: list of TransactionOutput.
        signature: signature (bytes) that verifies that the owner of the wallet (wallet1) created the transaction.
    """

    def __init__(
        self,
        sender_address,
        receiver_address,
        amount,
        previous_outputs,
        nbc_sent,
        signature=None,
    ):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_id = int.from_bytes(
            sha256(
                (
                    str(sender_address) + str(receiver_address) + str(amount)
                ).encode()
            ).digest(),
            byteorder="big",
        )
        self.nbc_sent = nbc_sent
        self.transaction_inputs = previous_outputs
        self.transaction_outputs = self.compute_transaction_output()
        self.signature = signature

    # Sign transaction with private key
    def sign_transaction(self, private_key):
        self.signature = pow(self.transaction_id, private_key.d, private_key.n)

    # Verify signature
    def verify_signature(self):
        if (
            pow(
                self.signature,
                self.sender_address["e"],
                self.sender_address["n"],
            )
            == self.transaction_id
        ):
            return True
        else:
            return False

    def compute_transaction_output(self):
        list_of_outputs = []
        list_of_outputs.append(
            {
                # receiver
                "transaction_id": self.transaction_id,
                "receiver_address": self.receiver_address,
                "amount": self.amount,
                "unspent": True,
            }
        )

        if self.nbc_sent > self.amount:
            list_of_outputs.append(
                {
                    # sender
                    "transaction_id": self.transaction_id,
                    "receiver_address": self.sender_address,
                    "amount": self.nbc_sent - self.amount,
                    "unspent": True,
                }
            )
        return list_of_outputs
