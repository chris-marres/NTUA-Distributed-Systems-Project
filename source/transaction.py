from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
import rsa
from hashlib import sha512

# import requests
# from flask import Flask, jsonify, request, render_template


import wallet
import hashlib


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
        value,
        previous_output_id,
        nbc_sent,
        signature=None,
    ):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = value
        self.transaction_id = int.from_bytes(
            sha512(
                (str(sender_address) + str(receiver_address) + str(value)).encode()
            ).digest(),
            byteorder="big",
        )
        self.nbc_sent = nbc_sent
        self.transaction_inputs = previous_output_id
        self.transaction_outputs = self.compute_transaction_output()
        self.signature = signature

    # Sign transaction with private key
    def sign_transaction(self, private_key):
        self.signature = pow(self.transaction_id, private_key.d, private_key.n)

    # Verify signature
    def verify_signature(self):
        if (
            pow(self.signature, self.sender_address["e"], self.sender_address["n"])
            == self.transaction_id
        ):
            return True
        else:
            return False

    def compute_transaction_output(self):
        list_of_outputs = []
        output = {}
        output["transaction_id"] = self.transaction_id
        output["receiver_address"] = self.receiver_address
        output["amount"] = self.amount
        output["unspent"] = True
        list_of_outputs.append(output)

        if self.nbc_sent > self.amount:
            # If sender has sent more money than needed
            sender_output = {}
            sender_output["transaction_id"] = self.transaction_id
            sender_output["receiver_address"] = self.receiver_address
            sender_output["amount"] = self.nbc_sent - self.amount
            sender_output["unspent"] = True
            list_of_outputs.append(sender_output)
        return list_of_outputs
