class TransactionInput:

    """
    The transaction input of a noobcash transaction.
    Each transaction input contains the attributes below:
        previous_output_id: id (int) of the transaction that the coins come from.
    """

    def __init__(self, previous_output_id):
        self.previous_output_id = previous_output_id