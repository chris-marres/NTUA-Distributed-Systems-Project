from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
import rsa
from hashlib import sha512

#import requests
#from flask import Flask, jsonify, request, render_template


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

    def __init__(self, sender_address, receiver_address, value, previous_output_id, signature = ('').encode()):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = value
        self.transaction_id = int.from_bytes(sha512((str(sender_address) + str(receiver_address) + str(value)).encode()).digest(), byteorder='big')
        # and convert back to SHA256 object
        # self.transaction_id = SHA256.new(binascii.unhexlify(self.transaction_id_str))
        # self.transaction_id_not_hex = hashlib.sha256((str(sender_address) + str(receiver_address)+str(value) + str(self.rand)).encode())
        # self.transaction_id = self.transaction_id_not_hex.hexdigest()
        self.transaction_inputs = previous_output_id
        self.transaction_outputs = []
        self.signature = signature

    # Sign transaction with private key
    def sign_transaction(self, private_key):
        self.signature = pow(self.transaction_id, private_key.d, private_key.n)
                                     
        
    # Verify signature
    def verify_signature(self):
        if pow(self.signature, self.sender_address['e'], self.sender_address['n']) == self.transaction_id:
            return True
        else:
            return False

            