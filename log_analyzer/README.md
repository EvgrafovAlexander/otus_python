# Log Analyzer

При запуске считывает логи из директории (log_dir), выбирает лог с ближайшей датой,
формирует отчёт с ограничением числа записей (report_size),
после чего сохраняет полученный отчёт в директорию (report_size).
Для записи логов приложения необходимо указать полный путь до файла с логами
(log_file_path).
Параметр (err_perc_limit) отвечает за предельный порог ошибок в %,
при достижении которого анализ считается неудачным.

### Параметры:
| Param name         | Description                                       |
|-----------------------|--------------------------------------------|
|-config, --config_file_path | - Configuration file path               |
| -log, --log_dir       | - Log dir path                              |
| -rep, --report_dir    | - Reports dir path                     |
|-size, --report_size   | - Report size                       |
|-err,  --err_perc_limit   | - Error limit %                    |
|-path, --log_file_path | - Logging file path               |

### Пример запуска с настройками файла конфигурации:
```
log_analyzer.py -config ./config.ini
```
### Пример запуска с указанием параметров:
```
log_analyzer.py -log ./log/ -rep ./reports/ -size 1000 -err 50.0 -path ./log_analyzer.log
```

*Пример файла конфигурации*:
```
[DEFAULT]
REPORT_SIZE = 1000
REPORT_DIR = "./reports/"
LOG_DIR = "./log/"
ERROR_PERC_LIMIT = 50
```
