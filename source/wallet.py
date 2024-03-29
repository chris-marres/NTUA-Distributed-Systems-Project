from Crypto.PublicKey import RSA


class Wallet:

    """
    The wallet of a node in the network.
    Each block contains the attributes below:
            private_key: the private key of the node.
            public_key: the public key of the node.
                            address: the public key of the node, which serves as its address as well.
            transactions: list which contains the transactions of the node.
    """

    def __init__(self):
        self.private_key = RSA.generate(bits=2048)
        self.public_key = {"n": self.private_key.n, "e": self.private_key.e}
        self.address = self.public_key
        self.transactions = []

    @property
    def balance(self):
        total_amount = 0
        for trans in self.transactions:
            for output in trans.transaction_outputs:
                if (
                    output["receiver_address"]["n"] == self.address["n"]
                    and output["unspent"]
                ):
                    total_amount += output["amount"]

        return total_amount
