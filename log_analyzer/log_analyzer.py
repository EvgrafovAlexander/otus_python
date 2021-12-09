#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

COMMON_PATTERN = r'nginx-access-ui.log-\d\d\d\d\d\d\d\d.*'
DATE_PATTERN = r'\d\d\d\d\d\d\d\d'
REF_PATTERN = r'(GET|POST).*(HTTP)'


class LogAnalyzer():
    def __init__(self, log_dir, report_dir, file_name=None, is_gz=False, is_last_log_calc=True):
        self.log_dir = log_dir
        self.report_dir = report_dir
        self.file_name = file_name
        self.is_gz = is_gz
        self.is_last_log_calc = is_last_log_calc

    def get_report(self):
        if self.is_last_log_calc:
            last_log = self.__get_last_log()
            if last_log:
                requests, full_request_time, full_request_cnt = self.__parse_log(last_log)
                return self.__calc_stat(requests, full_request_time, full_request_cnt)
            else:
                logging.info('Отсутствуют логи для обработки.')

    def __get_last_log(self) -> Tuple[str, bool] or None:
        """
        Получение наименования файла последней записи логов интерфейса
        :return: name - наименование файла
                 is_gz - является ли *gz расширением
                 None - если ни одного подходящего файла не найдено
        """
        result = None
        for name in os.listdir(self.log_dir):
            found = re.search(COMMON_PATTERN, name)
            if found:
                date = re.search(DATE_PATTERN, found.group(0))
                if date:
                    date = datetime.strptime(date.group(0), "%Y%m%d")
                    if result:
                        if date > result[0]:
                            result = date, name, name[-2:] == 'gz'
                    else:
                        result = date, name, name[-2:] == 'gz'
        return result

    def __parse_log(self, last_log) -> Tuple[Dict[str, List[float]], int, int]:
        requests = dict()
        full_request_time, full_request_cnt, error_cnt = 0, 0, 0
        _, filename, is_gz = last_log
        read_params = self.log_dir + '/' + filename, 'rb'
        open_func = gzip.open(*read_params) if is_gz else open(*read_params)
        with open_func as log_file:
            for line in log_file:
                line_info = self.__line_parse(line)
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
        return requests, full_request_time, full_request_cnt

    @staticmethod
    def __line_parse(line: bytes) -> Tuple[str, float] or None:
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

    def __calc_stat(self, requests: dict, full_time: float, full_cnt: int) -> List[dict]:
        """
        Вычисление статистических показателей
        и подготовка результирующих данных
        :requests: словарь вида url-запрос: список request_time
        :full_time: общая длительность выполнения запросов
        :full_cnt: общее количество выполненных запросов

        :return: список с показателями по каждому url
        """
        stat = []
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

    def save_report(self, report: List[dict]) -> None:
        """
        Запись отчёта в html
        :report: сформированный отчёт

        :return: None
        """
        template = open(self.report_dir + '/report.html').read()
        report = re.sub('\$table_json', json.dumps(report), template)
        with open(self.report_dir + '/' + 'report_final.html', 'w') as report_file:
            report_file.write(report)


def main():
    analyzer = LogAnalyzer(config["LOG_DIR"], config["REPORT_DIR"])
    report = analyzer.get_report()
    analyzer.save_report(report)


if __name__ == "__main__":
    main()
