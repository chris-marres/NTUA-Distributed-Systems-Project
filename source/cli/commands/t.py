from config import node_port
from requests import request


def t(
    receiver_address: int,
    amount: int,
):
    """Creates a transaction that sends `amount` coins to
    `receiver_address`.
    """
    request(
        method="GET",
        url=(
            f"http://localhost:{node_port}/create_transaction"
            f"?receiver_address={receiver_address}"
            f"&amount={amount}"
        ),
    )

    print("Transaction created successfully!")
