#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import argparse, configparser
import gzip
import json
import logging
import os
import re
import statistics
import sys
from collections import namedtuple
from datetime import datetime
from typing import Dict, List, Tuple

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports/",
    "LOG_DIR": "./log/",
    "ERROR_PERC_LIMIT": 50,
    "LOG_FILE_PATH": None
}

Log = namedtuple('Log', 'date name path is_gz')

COMMON_PATTERN = r'^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$'
REF_PATTERN = r'(GET|POST).*(HTTP)'


def get_report(log: Log) -> Tuple[List[dict], float]:
    """
    Получение отчёта по ранее найденному логу
    :log: данные по логу

    :return: Отчёт, сортированный по убыванию
            времени обработки запроса
             Процент ошибок распознавания
    """
    if not log.name:
        return [], 0
    requests, full_request_time, full_request_cnt, error_cnt = parse_log(log)
    error_perc = 100 * error_cnt / full_request_cnt if full_request_cnt else 0

    return calc_stat(requests, full_request_time, full_request_cnt), error_perc


def get_last_log(log_dir: str) -> namedtuple or None:
    """
    Получение наименования файла последней записи логов интерфейса
    :log_dir: директория чтения логов

    :return: Tuple вида:
             date - дата записи лога
             name - наименование файла
             is_gz - является *gz расширением
    """
    last_log = None
    for name in os.listdir(log_dir):
        found = re.match(COMMON_PATTERN, name)
        if found:
            name = found.group(0)
            date = found.group(1)
            is_gz = found.group(2)

            try:
                date = datetime.strptime(date, "%Y%m%d")
            except ValueError:
                logging.error('Невозможно извлечь дату: %s', date)
                continue

            if not last_log or date > last_log.date:
                last_log = Log(date, name, log_dir, is_gz and True)

    return last_log


def parse_log(log: Log) -> Tuple[Dict[str, List[float]], int, int, int]:
    """
    Сбор информации по логу
    :log_dir: информация о рассматриваемом логе

    :return: requests - словарь вида url-запрос: список request_time
             full_time - общая длительность выполнения запросов
             full_cnt - общее количество выполненных запросов
             error_cnt - общее количество ошибок распознавания
    """
    requests = dict()
    full_request_time, full_request_cnt, error_cnt = 0, 0, 0
    read_params = os.path.join(log.path, log.name), 'rb'
    open_func = gzip.open(*read_params) if log.is_gz else open(*read_params)
    with open_func as log_file:
        for line in log_file:
            line_info = parse_line(line)
            if line_info:
                request, request_time = line_info
                if request not in requests:
                    requests[request] = [request_time]
                else:
                    requests[request].append(request_time)
                full_request_time += request_time
                full_request_cnt += 1
            else:
                error_cnt += 1
    return requests, full_request_time, full_request_cnt, error_cnt


def is_already_analyzed(log: Log, report_dir: str) -> bool:
    """
    Проверка на существование отчёта по данному логу
    :report_dir: информация о логе
    :report_dir: директория хранения отчётов

    :return: флаг наличия отчёта
    """
    path = os.path.join(report_dir, 'report-' + log.date.strftime("%Y.%m.%d") + '.html')
    return os.path.exists(path)


def parse_line(line: bytes) -> Tuple[str, float] or None:
    """
    Парсинг строки лога
    :line: строка лога

    :return: request - http-запрос
             request_time - длительность обработки запроса
             None - если не удалось распознать строку
        """
    line = line.decode('utf-8')
    found = re.search(REF_PATTERN, line)
    if found:
        request = found.group(0).split()[1]
        request_time = float(line.split()[-1])
        return request, request_time
    return None


def calc_stat(requests: dict, full_time: float, full_cnt: int) -> List[dict]:
    """
    Вычисление статистических показателей
    и подготовка результирующих данных
    :requests: словарь вида url-запрос: список request_time
    :full_time: общая длительность выполнения запросов
    :full_cnt: общее количество выполненных запросов

    :return: список с показателями по каждому url
    """
    stat = []

    if not full_cnt:
        logging.info('Не найдено ни одной записи в логе. Анализ остановлен.')
        return stat

    for request, times in requests.items():
        time_sum = sum(times)
        stat.append(
            {'url': request,
             'count': len(times),
             'count_perc': round(100 * len(times) / full_cnt, 3),
             'time_sum': round(time_sum, 3),
             'time_perc': round(100 * time_sum / full_time, 3),
             'time_avg': round(time_sum / len(times), 3),
             'time_max': round(max(times), 3),
             'time_med': round(statistics.median(times), 3)}
        )
    return stat


def save_report(log: namedtuple, report: List[dict], report_dir: str, report_size: int) -> None:
    """
    Запись отчёта в html
    :log: информация о файле логирования
    :report: сформированный отчёт
    :report_dir: директория для записи отчёта
    :report_size: максимальный размер отчёта

    :return: None
    """
    report.sort(key=lambda x: x['time_sum'], reverse=True)
    with open(os.path.join(report_dir, 'report.html')) as template:
        template = template.read()
    report = re.sub('\$table_json', json.dumps(report[:report_size]), template)

    with open(os.path.join(report_dir, 'report-' + log.date.strftime("%Y.%m.%d") + '.html'), 'w') as report_file:
        report_file.write(report)


def set_config(args, conf_default: dict) -> dict:
    """
    Настройка конфигурации с приоритетом
    по убыванию "из файла config -> из переданных параметров -> по умолчанию"
    :param args: аргументы пользователя
    :param conf_default: конфигурация по умолчанию

    :return: словарь конфигурации с ключами:
             LOG_DIR - директория чтения логов
             REPORT_DIR - директория записей отчёта
             REPORT_SIZE - предельный размер отчёта
             ERROR_PERC_LIMIT - предельный % ошибок
             LOG_FILE_PATH - путь до файла с логом
    """
    if args.config_file_path:
        # config из файла
        try:
            conf = configparser.ConfigParser()
            conf.read(args.config_file_path)

            report_size = int(conf['DEFAULT']['REPORT_SIZE'])
            report_dir = conf['DEFAULT']['REPORT_DIR']
            log_dir = conf['DEFAULT']['LOG_DIR']
            err_perc_limit = float(conf['DEFAULT']['ERROR_PERC_LIMIT'])
            log_file_path = conf['DEFAULT']['LOG_FILE_PATH']

        except Exception as e:
            logging.exception('Возникло исключение при чтении конфигурационного файла %s, %s', type(e), e.args)
            sys.exit(1)
    else:
        # config из параметров
        report_size = int(args.report_size) if args.report_size else conf_default['REPORT_SIZE']
        report_dir = args.report_dir if args.report_dir else conf_default['REPORT_DIR']
        log_dir = args.log_dir if args.log_dir else conf_default['LOG_DIR']
        err_perc_limit = float(args.err_perc_limit) if args.err_perc_limit else conf_default['ERROR_PERC_LIMIT']
        log_file_path = args.log_file_path if args.log_file_path else conf_default['LOG_FILE_PATH']

    logging.info('Директория чтения логов: %s', log_dir)
    logging.info('Директория записи отчётов: %s', report_dir)
    logging.info('Предельный размер отчёта: %i', report_size)
    logging.info('Предельный %% ошибок: %.1f', err_perc_limit)

    config = {'LOG_DIR': log_dir,
              'REPORT_DIR': report_dir,
              'REPORT_SIZE': report_size,
              'ERROR_PERC_LIMIT': err_perc_limit,
              'LOG_FILE_PATH': log_file_path}

    return config


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-log', "--log_dir", type=str, help="Log dir path example: ./log/")
    parser.add_argument('-rep', "--report_dir", type=str, help="Reports dir path example: ./reports/")
    parser.add_argument('-size', "--report_size", type=int, help="Report size example: 1000")
    parser.add_argument('-err', "--err_perc_limit", type=float, help="Error limit % example: 50.0")
    parser.add_argument('-path', "--log_file_path", type=str, help="Logging file path: ./log_analyzer.log")
    parser.add_argument('-config', "--config_file_path", type=str, help="Configuration file path: ./config.ini")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    config = set_config(args, default_config)

    logging.basicConfig(format='[%(asctime)s] %(levelname).1s:%(message)s',
                        level=logging.DEBUG,
                        datefmt='%Y.%m.%d %H:%M:%S',
                        filename=config['LOG_FILE_PATH'])
    try:
        log = get_last_log(config['LOG_DIR'])

        if not log:
            logging.info('Отсутствуют логи для обработки. Анализ остановлен.')
        elif is_already_analyzed(log, config['REPORT_DIR']):
            logging.info('Отчёт по последнему логу уже существует. Анализ остановлен.')
        else:
            report, error_perc = get_report(log)

            if error_perc > config['ERROR_PERC_LIMIT']:
                logging.info('Превышение порога ошибок парсинга: %s %% > %s %%. Анализ остановлен',
                             round(error_perc, 1), config['ERROR_PERC_LIMIT'])

            if report:
                save_report(log, report, config['REPORT_DIR'], config['REPORT_SIZE'])

    except Exception as e:
        logging.exception('Необработанное исключение %s, %s', type(e), e.args)


if __name__ == "__main__":
    main()
