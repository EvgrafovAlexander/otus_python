# OTUServer

### Нагрузочное тестирование:
1. Запустить сервер, выполнив ```httpd.py```;
2. В консоли выполнить: 
```ab -n 50000 -c 100 -r http://localhost:9000/```

### Результаты тестирования:

Server Software:        Python

Server Hostname:        localhost

Server Port:            9000

Document Path:          /

Document Length:        0 bytes

Concurrency Level:      15

Time taken for tests:   107.000 seconds

Complete requests:      50000

Failed requests:        2
   (Connect: 0, Receive: 2, Length: 0, Exceptions: 0)

Non-2xx responses:      49998

Total transferred:      4949802 bytes

HTML transferred:       0 bytes

Requests per second:    467.29 [#/sec] (mean)

Time per request:       32.100 [ms] (mean)

Time per request:       2.140 [ms] (mean, across all concurrent requests)

Transfer rate:          45.18 [Kbytes/sec] received


| Connection Times (ms)      | min | mean | [+/-sd] | median | max   |
|---------------------|-----|------|---------|--------|-------|
|Connect     | 0   | 17   | 527.7   | 0      | 19691 |
|Processing     | 10  | 15   | 16.7    | 13     | 281   |
|Waiting     | 0   | 15   | 16.5    | 13     | 281   |
|Total     | 10  | 32   | 528.2   | 14     | 19704 |
