class Blockchain:

    """
    The blockchain of the noobcash.
    The blockchain contains the attributes below:
        blocks: list of blocks that have been validated.
    """

    def __init__(self):
        self.blocks = []

    # Add a validated block in the blockchain
    def add_block(self, block):
        self.blocks.append(block)

    def get_next_index(self):
        return len(self.blocks)

    def get_previous_hash(self):
        if len(self.blocks) != 0:
            return self.blocks[-1].current_hash
        else:
            return 1
