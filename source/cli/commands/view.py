from pprint import pprint

from config import node_port
from requests import request


def view():
    """Prints/Returns the transactions of the last block in the node's chain."""
    response = request(
        method="GET",
        url=f"http://localhost:{node_port}/view_transactions",
    )

    pprint(response.json()["transactions"])
