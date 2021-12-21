import os
import shutil
import unittest

from datetime import datetime

import log_analyzer


class TestLogAnalyzer(unittest.TestCase):

    def setUp(cls) -> None:
        cls.log_dir = './test_log/'
        cls.report_dir = './test_reports/'
        cls.report_size = 100

        for dir in (cls.log_dir, cls.report_dir):
            os.makedirs(dir, exist_ok=True)

        cls.log_fst = """"GET /api/v2 HTTP/1.1' 200 927 '-' 'Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 G' 0.390 \
                    'GET /api/1/photogenic_banners HTTP/1.1' 200 12 '-' 'Python-urllib/2.7' '-' '140' '-' 0.133 \
                    'GET /api/v2/banner HTTP/1.1' 200 19415 '-' 'Slotovod' '-' '1498697422-2118016444-4708-' 0.199
                    "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 " "-"  0.704
                    "GET /api/v2/internal/banner/2 HTTP/1.1" 200 407 "-" "-" "-" "146" "89f7f1be37d" 0.146
                    "GET /api/v2/group/ HTTP/1.1" 200 1020 "-" "Configovod" "-" "1447" "712e90144abee9" 0.628
                    "GET /api/v2/group/ HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "146-4708-9752772" "8b" 0.067
                    "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "149-9752771" "712e90e9" 0.138"""

        cls.expected_report = [{'url': '/api/v2', 'count': 1, 'count_perc': 16.667, 'time_sum': 0.199,
                                'time_perc': 10.574, 'time_avg': 0.199, 'time_max': 0.199, 'time_med': 0.199},
                               {'url': '/api/v2/slot/4705/groups', 'count': 1, 'count_perc': 16.667, 'time_sum': 0.704,
                                'time_perc': 37.407, 'time_avg': 0.704, 'time_max': 0.704, 'time_med': 0.704},
                               {'url': '/api/v2/internal/banner/2', 'count': 1, 'count_perc': 16.667, 'time_sum': 0.146,
                                'time_perc': 7.758, 'time_avg': 0.146, 'time_max': 0.146, 'time_med': 0.146},
                               {'url': '/api/v2/group/', 'count': 2, 'count_perc': 33.333, 'time_sum': 0.695,
                                'time_perc': 36.929, 'time_avg': 0.348, 'time_max': 0.628, 'time_med': 0.348},
                               {'url': '/api/v2/banner/1717161', 'count': 1, 'count_perc': 16.667, 'time_sum': 0.138,
                                'time_perc': 7.333, 'time_avg': 0.138, 'time_max': 0.138, 'time_med': 0.138}]

        with open(cls.log_dir + 'nginx-access-ui.log-20210929', 'w') as log_file:
            log_file.write(cls.log_fst)

        with open(cls.log_dir + 'nginx-access-ui.log-20211025.br2', 'w') as log_file:
            log_file.write('')

    def tearDown(cls) -> None:
        for dir in (cls.log_dir, cls.report_dir):
            shutil.rmtree(dir, ignore_errors=True)

    def test_log_analyzer(self):
        log = log_analyzer.get_last_log(self.log_dir)
        report, error_perc = log_analyzer.get_report(log)
        self.assertEqual(datetime(2021, 9, 29), log.date)
        self.assertListEqual(self.expected_report, report)


if __name__ == '__main__':
    unittest.main()
