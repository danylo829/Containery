from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse, urljoin

def format_docker_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return dt.strftime("%H:%M %d-%m-%Y")

def format_unix_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def stable_hash(value):
    return int(sha256(value.encode()).hexdigest(), 16) % (10**8)  # Limit the size of the hash

def is_safe_url(target: str, host_url: str) -> bool:
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def bytes_to_human_readable(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"
