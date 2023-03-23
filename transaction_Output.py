class TransactionOutput:

    """
    A transaction output of a noobcash transaction.
    Each transaction output contains the attributes below:
        transaction_id: the id (int) of the transaction.
        receiver: the receiver of the transaction.
        amount: the amount of nbcs (int) to be transfered.
        unspent: boolean variable that show if this output has been used as input in a transaction (False) or not (True).
    """

    def __init__(self, transaction_id, receiver, amount):
        self.transaction_id = transaction_id
        self.receiver = receiver
        self.amount = amount
        self.unspent = True