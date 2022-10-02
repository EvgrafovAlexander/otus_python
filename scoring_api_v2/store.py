import json
import logging
import time

import redis


class Store:
    def __init__(
        self, host="localhost", port=6379, db=0, sock_timeout=1, sock_conn_timeout=1, retry_counts=3, retry_timeout=1
    ):
        self._store = redis.Redis(
            host=host, port=port, db=db, socket_connect_timeout=sock_conn_timeout, socket_timeout=sock_timeout
        )
        self.retry_counts = retry_counts
        self.retry_timeout = retry_timeout

    def cache_get(self, key):
        try:
            val = self._store.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logging.exception("Get value from Redis error: %s" % e)
            return None

    def cache_set(self, key, value, storage_time):
        try:
            self._store.set(key, json.dumps(value), ex=storage_time)
        except Exception as e:
            logging.exception("Set value to Redis error: %s" % e)

    def get(self, key):
        for i in range(1, self.retry_counts + 1):
            try:
                val = self._store.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                logging.exception("Invalid connection, retry: %i" % i)
                time.sleep(self.retry_timeout)
                if i == self.retry_counts:
                    raise ConnectionError
