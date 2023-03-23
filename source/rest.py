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

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

load_dotenv(".env")

app = FastAPI()

port = 8000
clients_connected = 0
client_public_keys = []
client_ports = []
client_ips = []

class ClientConnection(BaseModel):
    public_key: str

@app.post("/client_connection")
def client_connection(client_connection: ClientConnection, request: Request):
    global port
    global clients_connected
    global client_public_keys
    global client_ports
    global client_ips

    port = port + 1
    client_ports.append(port)
    client_ips.append(request.client.host)

    clients_connected += 1
    client_public_keys.append(client_connection.public_key)

    print(f"Client connected: {client_connection.public_key}")
    print(f"Total clients connected: {clients_connected}")
    print(f"Client ports: {client_ports}")
    print(f"Client ips: {client_ips}")

    print(f"A new client connected to the network. Total clients connected: {clients_connected}")

    return {"id": clients_connected, "port": port}

if __name__ == "__main__":

    args = sys.argv[1:]
    print(args)

    if args[0] == "bootstrap":
        print("Starting bootstrap node")
        uvicorn.run("rest:app", host="0.0.0.0", port=port, reload=True)

    elif args[0] == "client":
        # connect to bootstrap node
        obj = {"public_key": 123}
        response = requests.post("http://192.168.0.2:8000/client_connection", json=obj).json()
        print(response)

        # start client node
        print("Starting client node")
        uvicorn.run("rest:app", host="0.0.0.0", port=response['port'], reload=True)
