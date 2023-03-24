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

    
         
         