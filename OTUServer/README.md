# OTUServer

Реализация web-сервера, частично реализующего протокол HTTP:
- принимает к обработке GET/HEAD запросы;
- реализована возможность передачи файлов по произвольному пути в
DOCUMENT_ROOT (пример: http://localhost:9000/httptest/dir1/dir12/dir123/deep.txt);
- DOCUMENT_ROOT задается при запуске сервера аргументом -r;
- Если вместо имени файла указана директория, происходит передача файла index.html,
находящегося в данной директории (пример: http://localhost:9000/httptest/dir2/);
- В случае успещного запроса сервер возвращает ответ структурного вида:

```
HTTP/1.1 200 OK\r\n
Date: Mon Oct 10 19:04:02 2022\r\n
Server: Python 3.10\r\n
Content-Length: 34\r\n
Content-Type: text/html\r\n
Connection: Closed\r\n\r\n
<html>Directory index file</html>\n
```

- В случае возникновения ошибки ответ выглядит следующим образом:
```
HTTP/1.1 404 Not Found
Date: Mon Oct 10 19:06:40 2022
Server: Python 3.10
Connection: Closed
```

### Запуск сервера
Для запуска необходимо передать аргументы:
- путь до папки root;
- адрес сервера;
- порт сервера;
- количество воркеров.

Пример:

```-r /OTUServer -port 9000 -addr 0.0.0.0 -w 4```

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
