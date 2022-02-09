import redis
import json


class Store:
    def __init__(self, host='localhost', port=6379, db=0):
        self._store = redis.Redis(host=host,
                                  port=port,
                                  db=db)

    def cache_get(self, key):
        val = self._store.get(key)
        if val:
            return json.loads(val)
        return None

    def cache_set(self, key, value, storage_time):
        self._store.set(key, json.dumps(value), ex=storage_time)

    # TODO: Доработать метод
    def get(self, key):
        try:
            val = self._store.get(key)
            if val:
                return json.loads(val)
        except:
            raise redis.exceptions.RedisError
