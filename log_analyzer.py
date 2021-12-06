#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import logging
import os
import re
from datetime import datetime
from typing import List, Tuple

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

COMMON_PATTERN = r'nginx-access-ui.log-\d\d\d\d\d\d\d\d.*'
DATE_PATTERN = r'\d\d\d\d\d\d\d\d'
REF_PATTERN = r'(GET|POST).*(HTTP)'


def main():
    last_log = get_last_log()
    if last_log:
        requests = dict()
        full_request_time, full_request_cnt, error_cnt = 0, 0, 0
        _, filename, is_gz = last_log
        read_params = config['LOG_DIR'] + '/' + filename, 'rb'
        open_func = gzip.open(*read_params) if is_gz else open(*read_params)
        with open_func as log_file:
            for line in log_file:
                line_info = line_parse(line)
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
        log_stat = calc_stat(requests, full_request_time, full_request_cnt)
    else:
        logging.info('Отсутствуют логи для обработки.')


def get_last_log() -> Tuple[str, bool] or None:
    """
    Получение наименования файла последней записи логов интерфейса
    :return: name - наименование файла
             is_gz - является ли *gz расширением
             None - если ни одного подходящего файла не найдено
    """
    result = None
    for name in os.listdir(config['LOG_DIR']):
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


def line_parse(line: bytes) -> Tuple[str, float] or None:
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


def calc_stat(requests: dict, full_time: float, full_cnt: int):
    """
    Вычисление статистических показателей
    и подготовка результирующих данных
    :requests: словарь вида url-запрос: список request_time
    :full_time: общая длительность выполнения запросов
    :full_cnt: общее количество выполненных запросов

    :return: request - http-запрос
             request_time - длительность обработки запроса
             None - если не удалось распознать строку
    """
    stat = []
    for request, times in requests.items():
        time_sum = sum(times)
        stat.append(
            {'url': request,
             'count': len(times),
             'count_perc': 100 * len(times) / full_cnt,
             'time_sum': time_sum,
             'time_perc': 100 * time_sum / full_time,
             'time_avg': time_sum / len(times),
             'time_max': max(times),
             'time_med': get_median(times)}
        )
    return stat


def get_median(values: List[float]) -> float:
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
        return (values[first] + values[first-1]) / 2


if __name__ == "__main__":
    main()
