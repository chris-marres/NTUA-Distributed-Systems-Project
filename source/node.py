import itertools
import json
from collections import deque
from copy import deepcopy
from threading import Lock, Thread
from time import sleep

import glob_variables as gb
import requests
from block import Block
from blockchain import Blockchain
from converters import convert_block_to_json, convert_transaction_to_json
from transaction import Transaction
from wallet import Wallet


def run_async(func, *args):
    thread = Thread(target=func, args=args)
    thread.start()


def post_async(**kwargs):
    thread = Thread(target=requests.post, kwargs=kwargs)
    thread.start()


class Node:
    def __init__(self):
        self.id = None
        self.nbc = 0
        self.chain = Blockchain()
        self.wallet = Wallet()
        # Ring: information regarding the id, ip, port, public key and balance of every node
        self.current_block = Block()
        self.ring = {}
        self.unconfirmed_blocks = deque()
        self.filter_lock = Lock()
        self.chain_lock = Lock()
        self.block_lock = Lock()
        self.stop_mining = False
        self.im_mining = False

    def register_node_to_ring(self, id, ip, port, public_key, balance):
        self.ring[int(public_key["n"])] = {
            "id": id,
            "ip": ip,
            "port": port,
            "public_key": public_key,
            "balance": balance,
        }

    def create_transaction(self, receiver, amount):
        print("Creating transaction", flush=True)
        # check if this node has enough money to spend
        trans_input = []
        nbcs = 0

        for trans in self.wallet.transactions:
            for output in trans.transaction_outputs:
                if (
                    output["receiver_address"]["n"] == self.wallet.address["n"]
                    and output["unspent"]
                ):
                    nbcs += output["amount"]
                    output["unspent"] = False
                    trans_input.append(output)
                if nbcs >= amount:
                    break

        if nbcs < amount:
            for output in trans_input:
                output["unspent"] = True
            print(
                "The sender node does not have enough money to spend for this transaction :/"
            )
            return False

        trans = Transaction(
            self.wallet.address, receiver, amount, trans_input, nbcs
        )
        print("Transaction created", flush=True)
        trans.sign_transaction(self.wallet.private_key)
        print("Transaction signed", flush=True)

        print("Broadcasting transaction", flush=True)
        run_async(self.broadcast_transaction, trans)
        print("Transaction broadcasted", flush=True)

        self.add_transaction_to_block(trans)

        return True

    def add_init_transaction(self):
        trans = Transaction(
            "0",
            self.wallet.address,
            gb.participants * 100,
            [],
            gb.participants * 100,
        )
        trans.sign_transaction(self.wallet.private_key)
        self.add_transaction_to_block(trans)

        return True

    def broadcast_transaction(self, transaction):
        print("Sending transaction:", flush=True)
        for node in self.ring.values():
            if node["id"] != self.id:
                transaction_packet = convert_transaction_to_json(transaction)

                post_async(
                    url=(
                        "http://"
                        + node["ip"]
                        + ":"
                        + str(node["port"])
                        + "/receive_transaction"
                    ),
                    json=transaction_packet.serialized,
                )

    def validate_transaction(self, trans: Transaction):
        # check if the signature is valid
        if not trans.verify_signature():
            print("The signature is not valid", flush=True)
            return False

        # check if sender has enough money
        if self.ring[trans.sender_address["n"]]["balance"] >= trans.amount:
            # create the 2 transaction outputs and add them in UTXOs list.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            return True
        print("There are not enough money to be spent", flush=True)
        return False

    def add_transaction_to_block(self, trans):
        # add transaction to the list of transactions of the sender and the receiver node
        if (
            trans.sender_address == self.wallet.public_key
            or trans.receiver_address == self.wallet.public_key
        ):
            self.wallet.transactions.append(trans)

        # update the balance of the sender and the receiver
        for ring_node in self.ring.values():
            if ring_node["public_key"] == trans.sender_address:
                ring_node["balance"] -= trans.amount
            if ring_node["public_key"] == trans.receiver_address:
                ring_node["balance"] += trans.amount

        self.block_lock.acquire()
        # if after adding this transaction, block is not yet full
        if (
            not self.current_block.add_transaction(trans)
            and trans.sender_address != "0"
        ):
            self.block_lock.release()
            return
        # if block is now full, start the mining procedure

        self.im_mining = True
        # First, add the current block in the queue of unconfirmed blocks
        self.unconfirmed_blocks.append(deepcopy(self.current_block))
        self.current_block = Block()
        self.block_lock.release()
        while True:
            print("Waiting for mining to finish", flush=True)
            with self.filter_lock:
                if self.unconfirmed_blocks:
                    mined_block = self.unconfirmed_blocks.popleft()
                    mining_result = self.mine_block(mined_block)
                    if mining_result:
                        # TODO: If mining stops from stop_mining, we
                        # need to keep the current block, not throw it
                        # away
                        break
                    else:
                        self.unconfirmed_blocks.appendleft(mined_block)
                else:
                    return
        self.im_mining = False

        if self.stop_mining:
            # TODO:
            self.stop_mining = False
        else:
            if self.broadcast_block(mined_block):
                self.validate_block(mined_block)

    def mine_block(self, block: Block):
        block.index = self.chain.get_next_index()
        block.previous_hash = self.chain.get_previous_hash()
        computed_hash = block.get_hash()

        if block.list_of_transactions[0].sender_address != "0":
            while (
                not computed_hash.startswith("0" * gb.mining_difficulty)
                and not self.stop_mining
            ):
                block.nonce += 1
                computed_hash = block.get_hash()
        block.current_hash = computed_hash

        return True

    def broadcast_block(self, block):
        print(block.current_hash, flush=True)

        good = False
        for node in self.ring.values():
            if node["id"] != self.id:
                block_packet = convert_block_to_json(block)

                response = requests.post(
                    "http://"
                    + node["ip"]
                    + ":"
                    + str(node["port"])
                    + "/receive_block",
                    json=block_packet.serialized,
                )
                if response.status_code == 200:
                    good = True

        return good

    def validate_block(self, block: Block):
        if block.previous_hash != "1":
            if not block.current_hash == block.get_hash():
                print(
                    "The current hash of this block is not correct", flush=True
                )
                return False

            if not block.previous_hash == self.chain.blocks[-1].current_hash:
                print(
                    "The previous block hash is different. There should be a",
                    "conflict",
                )
                return False

        self.chain.add_block(block)
        return True

    # consensus functions

    def filter_blocks(self, mined_block):
        with self.block_lock:
            total_transactions = list(
                itertools.chain.from_iterable(
                    [
                        unc_block.transactions
                        for unc_block in self.unconfirmed_blocks
                    ]
                )
            )
            if self.current_block:
                total_transactions.extend(self.current_block.transactions)
            self.current_block.transactions = []
            filtered_transactions = [
                transaction
                for transaction in total_transactions
                if (transaction not in mined_block.transactions)
            ]
            final_idx = 0
            if not self.unconfirmed_blocks:
                self.current_block.transactions = deepcopy(
                    filtered_transactions
                )
                return
            i = 0
            while (i + 1) * gb.capacity <= len(filtered_transactions):
                self.unconfirmed_blocks[i].transactions = deepcopy(
                    filtered_transactions[
                        i * gb.capacity : (i + 1) * gb.capacity
                    ]
                )
                i += 1
            if i * gb.capacity < len(filtered_transactions):
                self.current_block.transactions = deepcopy(
                    filtered_transactions[i * gb.capacity :]
                )

            for i in range(len(self.unconfirmed_blocks) - i):
                self.unconfirmed_blocks.pop()
        return

    def validate_chain(self, chain):
        blocks = chain.blocks
        for i in range(len(blocks)):
            if i == 0:
                if (
                    blocks[i].previous_hash != 1
                    or blocks[i].current_hash != blocks[i].get_hash()
                ):
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
        obj = json.dumps(self.ring)
        message = {"ring_json": obj}

        for node in self.ring.values():
            if node["id"] != self.id:
                response = requests.post(
                    "http://"
                    + node["ip"]
                    + ":"
                    + str(node["port"])
                    + "/receive_ring",
                    json=message,
                )

                if response.status_code != 200:
                    return False

        sleep(5)
        return True

    def resolve_conflicts(self, new_block):
        pass
