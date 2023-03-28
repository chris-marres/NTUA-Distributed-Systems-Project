import hashlib
import json

# Compute the SHA256 hash of a string
data = 'Hello, World!'



hash_object = hashlib.sha256(data.encode())
# Convert the hash bytes to a hexadecimal string
hex_digest = hash_object.hexdigest()
# Serialize the hash to JSON
hash_json = json.dumps({'hash': hex_digest})
# Deserialize the JSON string to a Python dictionary
hash_dict = json.loads(hash_json)
# Extract the hash value as a hexadecimal string
hex_digest = hash_dict['hash']
# Convert the hexadecimal string to bytes
byte_digest = bytes.fromhex(hex_digest)

# Create a new SHA256 hash object using the bytes
hash_object = hashlib.sha256(byte_digest)

# Print the hash value as a hexadecimal string
#print(hash_object.hexdigest())