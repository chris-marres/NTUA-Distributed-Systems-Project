from block import Block
from blockchain import Blockchain
from schema import BlockPacket, TransactionPacket
from transaction import Transaction


def convert_transaction_to_json(transaction: Transaction):
    return TransactionPacket(
        transaction_id=transaction.transaction_id,
        sender_address=transaction.sender_address,
        receiver_address=transaction.receiver_address,
        amount=transaction.amount,
        transaction_inputs=transaction.transaction_inputs,
        nbc_sent=transaction.nbc_sent,
        signature=transaction.signature,
    )


def convert_json_to_transaction(transaction: TransactionPacket):
    transaction = Transaction(
        transaction.sender_address,
        transaction.receiver_address,
        transaction.amount,
        transaction.transaction_inputs,
        transaction.nbc_sent,
        transaction.signature,
    )
    transaction.transaction_id = transaction.transaction_id

    return transaction


def convert_block_to_json(block: Block):
    transaction_packets = []
    for transaction in block.list_of_transactions:
        transaction_packet = convert_transaction_to_json(transaction)
        transaction_packets.append(transaction_packet)

    return BlockPacket(
        index=block.index,
        timestamp=block.timestamp,
        list_of_transactions=transaction_packets,
        nonce=block.nonce,
        current_hash=block.current_hash,
        previous_hash=block.previous_hash,
    )


def convert_json_to_block(block_packet: BlockPacket):
    transactions = []
    for transaction_packet in block_packet.list_of_transactions:
        transaction = convert_json_to_transaction(transaction_packet)
        transactions.append(transaction)

    block = Block()
    block.index = block_packet.index
    block.timestamp = block_packet.timestamp
    block.list_of_transactions = transactions
    block.nonce = block_packet.nonce
    block.current_hash = block_packet.current_hash
    block.previous_hash = block_packet.previous_hash

    return block


def convert_chain_to_json(chain: Blockchain):
    block_packets = []
    for block in chain.blocks:
        block_packet = convert_block_to_json(block).serialized
        block_packets.append(block_packet)

    return {
        "block_packets": block_packets,
        "total_block_time": chain.total_block_time,
        "block_counter": chain.block_counter,
        "previous_block_time": chain.previous_block_time,
    }


def convert_json_to_chain(
    block_jsons: list, total_block_time, previous_block_time, block_counter
):
    blocks = []
    for block_json in block_jsons:
        block_packet = BlockPacket(**block_json)
        block = convert_json_to_block(block_packet)
        blocks.append(block)

    chain = Blockchain(total_block_time, previous_block_time, block_counter)
    chain.blocks = blocks

    return chain
