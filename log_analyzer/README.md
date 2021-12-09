# Log Analyzer

При запуске считывает логи из директории (log_dir), выбирает лог с ближайшей датой,
формирует отчёт с ограничением числа записей (report_size),
после чего сохраняет полученный отчёт в директорию (report_size).
Для записи логов приложения необходимо указать полный путь до файла с логами
(log_file_path).

### Параметры:
| Name or flags         | Help                                       |
|-----------------------|--------------------------------------------|
| -log, --log_dir       | - Log dir path                              |
| -rep, --report_dir    | - Reports dir path                     |
|-size, --report_size   | - Report size                       |
|-path, --log_file_path | - Logging file path               |

### Пример запуска:
```
log_analyzer.py -log ./log/ -rep ./reports/ -size 1000 -path ./log_analyzer.log
```
