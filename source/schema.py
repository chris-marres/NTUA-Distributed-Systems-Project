from pydantic import BaseModel


class ClientConnection(BaseModel):
    public_key_json: str
    port: int
    id: int


class TransactionPacket(BaseModel):
    transaction_id: str
    sender_address: str | dict[str, int]
    receiver_address: str | dict[str, int]
    amount: int
    transaction_inputs: list
    nbc_sent: int
    signature: int

    @property
    def serialized(self):
        return {
            "transaction_id": self.transaction_id,
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount,
            "transaction_inputs": self.transaction_inputs,
            "nbc_sent": self.nbc_sent,
            "signature": self.signature,
        }


class RingPacket(BaseModel):
    ring_json: str


class BlockPacket(BaseModel):
    index: int
    timestamp: float
    list_of_transactions: list[TransactionPacket]
    nonce: int
    current_hash: str
    previous_hash: str

    @property
    def serialized(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "list_of_transactions": [
                transaction.serialized
                for transaction in self.list_of_transactions
            ],
            "nonce": self.nonce,
            "current_hash": self.current_hash,
            "previous_hash": self.previous_hash,
        }
