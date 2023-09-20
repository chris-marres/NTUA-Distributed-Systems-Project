import json
import sys
import threading
from queue import Queue
from time import sleep, time

import glob_variables as gb
import requests
import uvicorn
from converters import (
    convert_chain_to_json,
    convert_json_to_block,
    convert_json_to_transaction,
)
from fastapi import FastAPI, HTTPException, Request
from node import Node
from schema import BlockPacket, ClientConnection, RingPacket, TransactionPacket

app = FastAPI()

port = 8000
clients_connected = 0
node = Node()


@app.get("/chain/length")
def chain_length():
    global node

    return {"length": len(node.chain.blocks)}


@app.get("/chain")
def chain():
    global node

    return {"block_packets": convert_chain_to_json(node.chain)}


@app.get("/id_to_address")
def chain():
    global node

    return {"id_to_address": node.id_to_address}


@app.get("/get_ring")
def get_ring():
    global node

    return {"ring": node.ring}


@app.get("/create_transaction")
def create_transaction(receiver_address: int, amount: int):
    global node

    transaction = node.create_transaction(
        {"n": receiver_address, "e": 65537}, amount
    )

    return {"message": "Transaction created"}


@app.get("/view_transactions")
def view_transactions():
    global node

    return {"transactions": node.chain.blocks[-1].list_of_transactions}


@app.post("/receive_block")
def receive_block(block_packet: BlockPacket):
    global node

    block = convert_json_to_block(block_packet)

    node.chain_lock.acquire()
    if node.validate_block(block):
        node.stop_mining = True
        with node.filter_lock:
            node.chain.blocks.append(block)
            node.chain_lock.release()
            node.remove_double_transactions(block)
            node.stop_mining = False

    else:
        if block.current_hash == block.get_hash():
            if node.resolve_conflicts(block):
                node.stop_mining = True
                with node.filter_lock:
                    node.chain.blocks.append(block)
                    node.chain_lock.release()
                    node.remove_double_transactions(block)
                    node.stop_mining = False
            else:
                node.chain_lock.release()
                raise HTTPException(
                    status_code=400, detail="Block unacceptable"
                )

        else:
            node.chain_lock.release()
            raise HTTPException(
                status_code=400, detail="Block signature is not valid"
            )

    return {"status": "Block received and validated"}


@app.post("/receive_transaction")
def receive_transaction(transaction_packet: TransactionPacket):
    global node
    print("Received transaction", flush=True)

    transaction = convert_json_to_transaction(transaction_packet)
    if (
        transaction.transaction_id in node.upcoming_transaction_ids
        and transaction.sender_address != "0"
    ):
        if (
            transaction.sender_address == node.wallet.public_key
            or transaction.receiver_address == node.wallet.public_key
        ):
            node.wallet.transactions.append(transaction)

        # update the balance of the sender and the receiver
        for ring_node in node.ring.values():
            if ring_node["public_key"] == transaction.sender_address:
                ring_node["balance"] -= transaction.amount
            if ring_node["public_key"] == transaction.receiver_address:
                ring_node["balance"] += transaction.amount

        node.upcoming_transaction_ids.remove(transaction.transaction_id)
        raise HTTPException(
            status_code=400, detail="Transaction already processed"
        )

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


def start_transactions_thread():
    global node
    global transactions_total_time
    sleep(10)

    transactions_start_time = time()

    index = 0
    with open("/transactions/transactions.txt", "r") as infile:
        lines = infile.readlines()
        for line in lines:
            if index == 4:
                break
            receiver_id = int(line.split(" ")[0][-1])
            amount = int(line.split(" ")[1])

            print(f"Sending {amount} coins to client{receiver_id}", flush=True)

            node.create_transaction(
                node.id_to_address[receiver_id],
                amount,
            )
            index += 1

    transactions_total_time = time() - transactions_start_time
    print(f"Transactions Total time: {transactions_total_time}", flush=True)
    print(
        f"Transactions Average time: {transactions_total_time / index}",
        flush=True,
    )


@app.get("/start")
def start():
    threading.Thread(target=start_transactions_thread).start()
    return {"status": "Started"}


def start_client_transactions_thread():
    global node

    def get_start(queue, url):
        response = requests.get(url=url)
        queue.put(response)

    response_queue = Queue()
    threads = []
    for other_node in node.ring.values():
        if other_node["id"] == node.id:
            continue
        thread = threading.Thread(
            target=get_start,
            args=(
                response_queue,
                f"http://{other_node['ip']}:{str(other_node['port'])}/start",
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    start()


start_thread = threading.Thread(target=start_client_transactions_thread)


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
        node.register_node_to_ring(
            0, "bootstrap", 8000, node.wallet.address, 0
        )

        node.id_to_address = {
            value["id"]: value["public_key"] for value in node.ring.values()
        }

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

        start_thread.start()
    return {"id": client_connection.id, "port": client_connection.port}


@app.post("/receive_ring")
def receive_ring(ring: RingPacket, request: Request):
    global node

    # Parse JSON string into a dictionary
    ring_dict = json.loads(ring.ring_json)

    # Create ring object from dictionary
    node.ring = {int(key): value for key, value in ring_dict.items()}
    node.id_to_address = {
        value["id"]: value["public_key"] for value in node.ring.values()
    }

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
