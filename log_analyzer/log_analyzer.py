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
from collections import namedtuple
from datetime import datetime
from typing import Dict, List, Tuple


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports/",
    "LOG_DIR": "./log/",
    "ERROR_PERC_LIMIT": 50
}

Log = namedtuple('Log', 'date name path is_gz')

COMMON_PATTERN = r'nginx-access-ui.log-\d\d\d\d\d\d\d\d(.gz|)$'
DATE_PATTERN = r'\d\d\d\d\d\d\d\d'
REF_PATTERN = r'(GET|POST).*(HTTP)'


class LogAnalyzer():
    def __init__(self, log: Log):
        self.date = log.date
        self.name = log.name
        self.path = log.path
        self.is_gz = log.is_gz

    def get_report(self, err_perc_limit: float) -> List[dict]:
        """
        Получение отчёта по ранее найденному логу
        :err_perc_limit: предельный % ошибок

        :return: Отчёт, сортированный по убыванию
                времени обработки запроса
        """
        if not self.name:
            return []
        requests, full_request_time, full_request_cnt, error_cnt = self.__parse_log()
        return self.__calc_stat(requests, full_request_time, full_request_cnt, error_cnt, err_perc_limit)

    @staticmethod
    def get_last_log(log_dir: str, report_dir: str) -> namedtuple or None:
        """
        Получение наименования файла последней записи логов интерфейса
        :log_dir: директория чтения логов
        :report_dir: директория хранения отчётов

        :return: Tuple вида:
                 date - дата записи лога
                 name - наименование файла
                 is_gz - является *gz расширением
        """
        last_log = None
        for name in os.listdir(log_dir):
            found = re.search(COMMON_PATTERN, name)
            if found:
                date = re.search(DATE_PATTERN, found.group(0))
                if date:
                    date = datetime.strptime(date.group(0), "%Y%m%d")
                    if last_log:
                        if date > last_log.date:
                            last_log = Log(date, name, log_dir, name[-2:] == 'gz')
                    else:
                        last_log = Log(date, name, log_dir, name[-2:] == 'gz')
        if not last_log:
            logging.info('Отсутствуют логи для обработки. Анализ остановлен.')
        elif LogAnalyzer.is_already_analyzed(last_log, report_dir):
            last_log = None
            logging.info('Отчёт по последнему логу уже существует. Анализ остановлен.')

        return last_log

    def __parse_log(self) -> Tuple[Dict[str, List[float]], int, int, int]:
        """
        Сбор информации по логу

        :return: requests - словарь вида url-запрос: список request_time
                 full_time - общая длительность выполнения запросов
                 full_cnt - общее количество выполненных запросов
                 error_cnt - общее количество ошибок распознавания
        """
        requests = dict()
        full_request_time, full_request_cnt, error_cnt = 0, 0, 0
        read_params = self.path + self.name, 'rb'
        open_func = gzip.open(*read_params) if self.is_gz else open(*read_params)
        with open_func as log_file:
            for line in log_file:
                line_info = self.__parse_line(line)
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

    @staticmethod
    def is_already_analyzed(log: Log, report_dir: str) -> bool:
        """
        Проверка на существование отчёта по данному логу
        :report_dir: информация о логе
        :report_dir: директория хранения отчётов

        :return: флаг наличия отчёта
        """
        return 'report-' + log.date.strftime("%Y.%m.%d") + '.html' in os.listdir(report_dir)

    @staticmethod
    def __parse_line(line: bytes) -> Tuple[str, float] or None:
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

    def __calc_stat(self, requests: dict, full_time: float, full_cnt: int,
                    error_cnt: int, err_perc_limit: float) -> List[dict]:
        """
        Вычисление статистических показателей
        и подготовка результирующих данных
        :requests: словарь вида url-запрос: список request_time
        :full_time: общая длительность выполнения запросов
        :full_cnt: общее количество выполненных запросов
        :error_cnt: общее количество ошибок распознавания
        :err_perc_limit: предельный % ошибок

        :return: список с показателями по каждому url
        """
        stat = []

        if not full_cnt:
            logging.info('Не найдено ни одной записи в логе. Анализ остановлен.')
            return stat
        incorrect_perc = 100 * error_cnt / full_cnt
        if incorrect_perc > err_perc_limit:
            logging.info('Превышение порога ошибок парсинга:, %s %% > %s %%. Анализ остановлен',
                         round(incorrect_perc, 1), err_perc_limit)
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
                 'time_med': round(self.__get_median(times), 3)}
            )
        return stat

    @staticmethod
    def __get_median(values: List[float]) -> float:
        """
        Получение медианного значения
        :values: список request_time

        :return: медианное значение
        """
        values.sort()
        if len(values) % 2:
            return values[len(values) // 2]
        else:
            first = len(values) // 2
            return (values[first] + values[first - 1]) / 2

    @staticmethod
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
        with open(report_dir + 'report.html') as template:
            template = template.read()
        report = re.sub('\$table_json', json.dumps(report[:report_size]), template)
        with open(report_dir + '/' + 'report-' + log.date.strftime("%Y.%m.%d") + '.html', 'w') as report_file:
            report_file.write(report)


def config_setter(args, conf_default: dict):
    """
    Настройка конфигурации с приоритетом
    по убыванию "из файла config -> из переданных параметров -> по умолчанию"
    :param args: аргументы пользователя
    :param conf_default: конфигурация по умолчанию

    :return: сформированные значения конфигурационных параметров:
             log_dir - директория чтения логов
             report_dir - директория записей отчёта
             report_size - предельный размер отчёта
             err_perc_limit - предельный % ошибок
    """
    if args.config_file_path:
        # config из файла
        conf = configparser.ConfigParser()
        conf.read(args.config_file_path)

        report_size = int(conf['DEFAULT']['REPORT_SIZE']) if 'REPORT_SIZE' in conf['DEFAULT']\
            else conf_default['REPORT_SIZE']
        report_dir = conf['DEFAULT']['REPORT_DIR'] if 'REPORT_DIR' in conf['DEFAULT']\
            else conf_default['REPORT_DIR']
        log_dir = conf['DEFAULT']['LOG_DIR'] if 'LOG_DIR' in conf['DEFAULT']\
            else conf_default['LOG_DIR']
        err_perc_limit = float(conf['DEFAULT']['ERROR_PERC_LIMIT']) if 'ERROR_PERC_LIMIT' in conf['DEFAULT']\
            else config['ERROR_PERC_LIMIT']
    else:
        # config из параметров
        report_size = int(args.report_size) if args.report_size else conf_default['REPORT_SIZE']
        report_dir = args.report_dir if args.report_dir else conf_default['REPORT_DIR']
        log_dir = args.log_dir if args.log_dir else conf_default['LOG_DIR']
        err_perc_limit = float(args.err_perc_limit) if args.err_perc_limit else conf_default['ERROR_PERC_LIMIT']

    for dir in (log_dir, report_dir):
        os.makedirs(dir, exist_ok=True)

    logging.info('Директория чтения логов: %s', log_dir)
    logging.info('Директория записи отчётов: %s', report_dir)
    logging.info('Предельный размер отчёта: %i', report_size)
    logging.info('Предельный %% ошибок: %.1f', err_perc_limit)

    return log_dir, report_dir, report_size, err_perc_limit


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

    logging.basicConfig(format='[%(asctime)s] %(levelname).1s:%(message)s',
                        level=logging.DEBUG,
                        datefmt='%Y.%m.%d %H:%M:%S',
                        filename=args.log_file_path)

    try:
        log_dir, report_dir, report_size, err_perc_limit = config_setter(args, config)

        log = LogAnalyzer.get_last_log(log_dir, report_dir)
        if log:
            analyzer = LogAnalyzer(log)
            report = analyzer.get_report(err_perc_limit)
            if report:
                analyzer.save_report(log, report, report_dir, report_size)

    except Exception as e:
        logging.exception('Необработанное исключение %s, %s', type(e), e.args)


if __name__ == "__main__":
    main()
