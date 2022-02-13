# Scoring API



## Для запуска Redis:

1. Выполнить в docker:
*docker run -p 6379:6379 --name redis -d redis*

2. Установить пакет: pip install redis

3. Для проверки работы выполнить:

import redis

r = redis.Redis(host='localhost', port=6379)

r.set('foo', 'bar')

answer = r.get('foo')
