from config import node_port
from requests import request


def balance():
    """Prints/Returns the balance of the node's wallet."""
    response = request(
        method="GET",
        url=f"http://localhost:{node_port}/balance",
    )

    print(response.json()["balance"])
