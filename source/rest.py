"""
import block
import node
import wallet
import transaction
import wallet


import blockchain
blockchain = Blockchain()

#.......................................................................................

# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200



# run it once for every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
"""

import os
import sys
import json
import binascii

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
from Crypto.PublicKey import RSA

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

from node import Node
from transaction import Transaction
import glob_variables as gb

import time
import threading

load_dotenv(".env")

app = FastAPI()

port = 8000
clients_connected = 0
node = Node()


class ClientConnection(BaseModel):
    public_key_json: str
    port: int
    id: int


class TransactionPacket(BaseModel):
    transaction_json: str


@app.post("/receive_transaction")
async def receive_transaction(transaction: TransactionPacket, request: Request):
    global node

    # Parse JSON string into a dictionary
    transaction_dict = json.loads(transaction.transaction_json)

    transaction_dict["sender_address"] = {
        key: int(value)
        for key, value in json.loads(transaction_dict["sender_address"]).items()
    }
    transaction_dict["receiver_address"] = {
        key: int(value)
        for key, value in json.loads(transaction_dict["receiver_address"]).items()
    }

    transaction = Transaction(
        transaction_dict["sender_address"],
        transaction_dict["receiver_address"],
        transaction_dict["amount"],
        transaction_dict["transaction_inputs"],
        transaction_dict["nbc_sent"],
        transaction_dict["signature"],
    )
    transaction.transaction_id = transaction_dict["transaction_id"]

    print("Received transaction")

    if node.validate_transaction(transaction):
        node.add_transaction_to_block(transaction)
        return {"status": "Transaction received and validated"}
    else:
        return HTTPException(status_code=400, detail="Transaction is not valid")


@app.get("/get_next_available_port_and_id")
async def get_next_available_port_and_id():
    global port
    global clients_connected

    port += 1
    clients_connected += 1

    return {"id": clients_connected, "port": port}


@app.post("/client_connection")
async def client_connection(client_connection: ClientConnection, request: Request):
    global node

    # Receive public_key_json from the network
    # Parse JSON string into a dictionary
    public_key_dict = json.loads(client_connection.public_key_json)

    node.register_node_to_ring(
        client_connection.id,
        f"client{client_connection.id}",
        client_connection.port,
        public_key_dict,
        0,
    )

    print(
        f"Client will launch a node at address: client{client_connection.id}:{client_connection.port} with id {client_connection.id} and balance 0"
    )

    if len(node.ring) == gb.participants - 1:
        print("Initializing bootstrap node")
        node.id = 0
        node.register_node_to_ring(0, "bootstrap", 8000, node.wallet.address, 0)

        print("Creating genesis block")
        node.create_new_block()

        print("Create the first transaction. Money out of thin air!!")
        node.add_init_transaction()

        if node.broadcast_ring():
            # Send a transaction of 100 coins to all the clients
            for client in node.ring.values():
                if client["id"] != 0:
                    node.create_transaction(client["public_key"], 100)
        else:
            print("Ring broadcast failed")

        print(node.ring)

    return {"id": client_connection.id, "port": client_connection.port}


class RingPacket(BaseModel):
    ring_json: str


@app.post("/receive_ring")
async def receive_ring(ring: RingPacket, request: Request):
    global node

    # Parse JSON string into a dictionary
    ring_dict = json.loads(ring.ring_json)

    # Create ring object from dictionary
    node.ring = {int(key): value for key, value in ring_dict.items()}

    return {"status": "Ring received"}


def client_thread_function():
    global node
    global port

    time.sleep(5)
    # connect to bootstrap node
    # Export public key to a dictionary
    public_key_dict = {"n": node.wallet.address["n"], "e": node.wallet.address["e"]}

    # Convert dictionary to JSON string
    public_key_json = json.dumps(public_key_dict)

    # create object
    obj = {"public_key_json": public_key_json, "port": port, "id": node.id}

    # Send public_key_json over the network
    response = requests.post("http://bootstrap:8000/client_connection", json=obj).json()
    print(response)


@app.get("/balance")
async def balance():
    global node

    return {"balance": node.wallet.balance}


def main():
    global node
    global port

    args = sys.argv[1:]
    print(args)

    if args[0] == "bootstrap":
        print("Starting bootstrap node")
        node.id = 0
        print("Starting bootstrap node server")
        uvicorn.run(app=app, host="0.0.0.0", port=port)

    elif args[0] == "client":
        # start client node
        print("Starting client node")

        time.sleep(3 * int(args[1]))
        # get next available port and id
        response = requests.get(
            "http://bootstrap:8000/get_next_available_port_and_id"
        ).json()
        node.id = response["id"]
        port = response["port"]

        # create thread
        x = threading.Thread(target=client_thread_function, args=())
        x.start()

        # start client node server
        print("Starting client node server")
        uvicorn.run(app=app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
