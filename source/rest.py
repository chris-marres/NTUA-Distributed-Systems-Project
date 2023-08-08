import json
import sys
import threading
from time import sleep

import glob_variables as gb
import requests
import uvicorn
from converters import convert_json_to_block, convert_json_to_transaction
from fastapi import FastAPI, HTTPException, Request
from node import Node
from schema import BlockPacket, ClientConnection, RingPacket, TransactionPacket

app = FastAPI()

port = 8000
clients_connected = 0
node = Node()


@app.post("/receive_block")
def receive_block(block_packet: BlockPacket):
    global node

    block = convert_json_to_block(block_packet)

    if node.validate_block(block):
        node.stop_mining = True
        # remove double transactions from current block
        node.stop_mining = False

        return {"status": "Block received and validated"}

    raise HTTPException(status_code=400, detail="Block is not valid")


@app.post("/receive_transaction")
def receive_transaction(transaction_packet: TransactionPacket):
    global node

    transaction = convert_json_to_transaction(transaction_packet)

    if node.validate_transaction(transaction):
        node.add_transaction_to_block(transaction)
        return {"status": "Transaction received and validated"}
    else:
        raise HTTPException(status_code=400, detail="Transaction is not valid")


@app.get("/get_next_available_port_and_id")
def get_next_available_port_and_id():
    global port
    global clients_connected

    port += 1
    clients_connected += 1

    return {"id": clients_connected, "port": port}


@app.post("/client_connection")
def client_connection(client_connection: ClientConnection, request: Request):
    global node

    node.register_node_to_ring(
        client_connection.id,
        f"client{client_connection.id}",
        client_connection.port,
        client_connection.public_key,
        0,
    )

    print(
        f"Client will launch a node at address: client{client_connection.id}:{client_connection.port} with id {client_connection.id} and balance 0"
    )

    if len(node.ring) == gb.participants - 1:
        print("Initializing bootstrap node", flush=True)
        node.id = 0
        node.register_node_to_ring(0, "bootstrap", 8000, node.wallet.address, 0)

        print(
            "Create the first transaction. Money out of thin air!!", flush=True
        )
        node.add_init_transaction()
        sleep(gb.participants)

        if node.broadcast_ring():
            # Send a transaction of 100 coins to all the clients
            for client in node.ring.values():
                if client["id"] != 0:
                    node.create_transaction(client["public_key"], 100)
        else:
            print("Ring broadcast failed", flush=True)

    return {"id": client_connection.id, "port": client_connection.port}


@app.post("/receive_ring")
def receive_ring(ring: RingPacket, request: Request):
    global node

    # Parse JSON string into a dictionary
    ring_dict = json.loads(ring.ring_json)

    # Create ring object from dictionary
    node.ring = {int(key): value for key, value in ring_dict.items()}

    return {"status": "Ring received"}


def client_thread_function():
    global node
    global port

    sleep(gb.participants)
    # connect to bootstrap node
    # Export public key to a dictionary
    public_key = {
        "n": node.wallet.address["n"],
        "e": node.wallet.address["e"],
    }

    # create object
    obj = {"public_key": public_key, "port": port, "id": node.id}

    # Send public_key_json over the network
    response = requests.post(
        "http://bootstrap:8000/client_connection", json=obj
    ).json()
    print(response, flush=True)


@app.get("/balance")
def balance():
    global node

    return {"balance": node.wallet.balance}


@app.get("/start")
def start():
    with open("/transactions/transactions.txt", "r") as infile:
        lines = infile.readlines()
        for line in lines:
            print(line, flush=True)


@app.get("/test")
def test():
    global node

    return node.chain.__dict__


def main():
    global node
    global port

    args = sys.argv[1:]
    print(args, flush=True)

    if args[0] == "bootstrap":
        print("Starting bootstrap node", flush=True)
        node.id = 0
        print("Starting bootstrap node server", flush=True)
        uvicorn.run(app=app, host="0.0.0.0", port=port)

    elif args[0] == "client":
        # start client node
        print("Starting client node", flush=True)

        sleep(3 * int(args[1]))
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
        print("Starting client node server", flush=True)
        uvicorn.run(app=app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
