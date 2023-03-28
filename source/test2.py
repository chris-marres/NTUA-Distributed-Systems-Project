import rsa
import pickle

# create SHA-256 hash
msg_to_hash = 'hello'
trans_id = rsa.compute_hash(msg_to_hash.encode(), 'SHA-256')
serialized_data = pickle.dumps(trans_id)
received = pickle.loads(serialized_data)
print('Initial hash:', trans_id)
print('Received hash:', received)