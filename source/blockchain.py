import time


class Blockchain:

    """
    The blockchain of the noobcash.
    The blockchain contains the attributes below:
        blocks: list of blocks that have been validated.
    """

    def __init__(
        self, total_block_time=0, previous_block_time=None, block_counter=0
    ):
        self.blocks = []
        self.total_block_time = total_block_time
        self.previous_block_time = previous_block_time
        self.block_counter = block_counter

    # Add a validated block in the blockchain
    def add_block(self, block):
        self.blocks.append(block)

        if self.previous_block_time:
            self.block_counter += 1
            self.total_block_time += time.time() - self.previous_block_time
            self.previous_block_time = time.time()
        else:
            self.previous_block_time = time.time()

    def get_next_index(self):
        return len(self.blocks)

    def get_previous_hash(self):
        if len(self.blocks) != 0:
            return self.blocks[-1].current_hash
        else:
            return "1"
