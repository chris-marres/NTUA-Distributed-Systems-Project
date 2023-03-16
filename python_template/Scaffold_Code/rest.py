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

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(".env")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("rest:app", host="0.0.0.0", port=8000, reload=True)
