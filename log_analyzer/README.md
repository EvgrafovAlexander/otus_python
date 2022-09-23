# Log Analyzer

При запуске считывает логи из директории (log_dir), выбирает лог с ближайшей датой,
формирует отчёт с ограничением числа записей (report_size),
после чего сохраняет полученный отчёт в директорию (report_size).
Для записи логов приложения необходимо указать полный путь до файла с логами
(log_file_path).
Параметр (err_perc_limit) отвечает за предельный порог ошибок в %,
при достижении которого анализ считается неудачным.

### Аргументы:
| Arg name               | Description                                       |
|------------------------|--------------------------------------------|
| -config, --config_file_path | - Configuration file path               |

### Параметры:
| Param name       | Description                                       |
|---------------------|--------------------------------------------|
|LOG_DIR     | - Log dir path                              |
|REPORT_DIR    | - Reports dir path                     |
|REPORT_SIZE  | - Report size                       |
|ERROR_PERC_LIMIT | - Error limit %                    |
|LOG_FILE_PATH | - Logging file path               |

### *Пример запуска с настройками файла конфигурации*:
```
log_analyzer.py -config ./config.ini
```

### *Пример файла конфигурации*:
```
[DEFAULT]
REPORT_SIZE = 1000
REPORT_DIR = "./reports/"
LOG_DIR = "./log/"
LOG_FILE_PATH="./log_file/logfile.log"
ERROR_PERC_LIMIT = 50
```
