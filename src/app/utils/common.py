from datetime import datetime
from hashlib import sha256

def format_docker_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return dt.strftime("%H:%M %d-%m-%Y")

def format_unix_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def stable_hash(value):
    return int(sha256(value.encode()).hexdigest(), 16) % (10**8)  # Limit the size of the hash
