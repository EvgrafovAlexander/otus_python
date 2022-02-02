import redis


class Store:
    def __init__(self, host='localhost', port=6379, db=0):
        self._store = redis.Redis(host=host, port=port, db=db)

    def cache_get(self, key):
        return self._store.get(key)

    def cache_set(self, key, value, storage_time):
        self._store.set(key, value, ex=storage_time)
