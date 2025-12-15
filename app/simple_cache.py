import time

cache_storage = {}

def save_to_cache(key, value, ttl_seconds=1800):
    cache_storage[key] = {
        'value': value,
        'expires_at': time.time() + ttl_seconds
    }
    return True

def get_from_cache(key):
    if key in cache_storage:
        data = cache_storage[key]
        if time.time() < data['expires_at']:
            return data['value']
        else:
            del cache_storage[key]
    return None

def make_cache_key(*args):
    parts = [str(arg).replace(" ", "_") for arg in args]
    return "_".join(parts)

def clear_cache():
    count = len(cache_storage)
    cache_storage.clear()
    return count

def get_cache_stats():
    now = time.time()
    total = len(cache_storage)
    active = 0
    
    for key, data in cache_storage.items():
        if now < data['expires_at']:
            active += 1
    
    return {
        "total_entries": total,
        "active_entries": active,
        "expired_entries": total - active
    }

def cleanup_expired():
    now = time.time()
    expired_keys = []
    
    for key, data in cache_storage.items():
        if now >= data['expires_at']:
            expired_keys.append(key)
    
    for key in expired_keys:
        del cache_storage[key]
    
    return len(expired_keys)
