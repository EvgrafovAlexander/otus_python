# stdlib
import email
import logging
import mimetypes
import os
import urllib.parse
from datetime import datetime
from io import StringIO

CODE_OK = 200
ERROR_FORBIDDEN = 403
ERROR_NOT_FOUND = 404
ERROR_NOT_ALLOWED = 405


class Request:
    ENABLED_METHODS = ("GET", "HEAD")
    HTTP_CODES = {
        CODE_OK: "OK",
        ERROR_FORBIDDEN: "Forbidden",
        ERROR_NOT_FOUND: "Not Found",
        ERROR_NOT_ALLOWED: "Method Not Allowed",
    }

    def __init__(self, request_bytes: bytes, document_root: str):
        self.request_bytes = request_bytes
        self.document_root = document_root

    def get_response(self) -> bytes:
        """
        Получение ответа на запрос.

        :return: response - ответ на полученный запрос
        """
        parsed_request_data = self._parse_request()
        response = self._form_response(parsed_request_data)
        return response

    def _parse_request(self) -> dict:
        """
        Извлечение данных из полученного запроса.

        :return: parsed_request_data - словарь с данными запроса
        """
        request_string = self.request_bytes.decode("utf-8")
        request, headers = request_string.split("\r\n", 1)
        method, req_url, http_ver = request.split(" ")
        message = email.message_from_file(StringIO(headers))
        headers = dict(message.items())
        parsed_request_data = {"method": method, "url": req_url, "ver": http_ver, "headers": headers}
        return parsed_request_data

    def _form_response(self, req_data: dict) -> bytes:
        """
        Формирование ответа на запрос.

        :param req_data: извлеченные из запроса данные
        :return: response - сформированный ответ
        """
        if req_data["method"] not in self.ENABLED_METHODS:
            return self._get_error_message(ERROR_NOT_ALLOWED)

        query = self._prepare_query(req_data["url"])
        path = self.document_root + query
        if not os.path.exists(path):
            return self._get_error_message(ERROR_NOT_FOUND)

        if os.path.isdir(path) and "index.html" in os.listdir(path):
            return self._get_message(req_data["method"], path + "index.html", ".html")

        if os.path.isfile(path):
            name, extension = os.path.splitext(path)
            return self._get_message(req_data["method"], path, extension)

        return self._get_error_message(ERROR_NOT_FOUND)

    @staticmethod
    def _prepare_query(query: str) -> str:
        """
        Подготовка URL.

        :param query: необработанный запрос
        :return: предобработанный запрос
        """
        query = urllib.parse.unquote(query)
        parsed_url = urllib.parse.urlparse(query)
        return parsed_url.path

    def _get_message(self, method: str, filepath: str, extension: str) -> bytes:
        """
        Формирование ответного сообщения.

        :param method: метод запроса
        :param filepath: путь до файла
        :param extension: расширение файла
        :return: сформированный ответ на запрос
        """
        try:
            with open(filepath, "rb") as f:
                content = f.read()
                content_len = len(content)
                content_type = mimetypes.types_map[extension]
                date = datetime.now().ctime()
                message = (
                    f"HTTP/1.1 {CODE_OK} {self.HTTP_CODES[CODE_OK]}\r\n"
                    f"Date: {date}\r\n"
                    f"Server: Python 3.10\r\n"
                    f"Content-Length: {content_len}\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Connection: Closed\r\n\r\n"
                )
                message = str.encode(message)
                if method == "GET":
                    message += content
                logging.info("Response status: %s", str(CODE_OK))
                return message
        except Exception:
            return self._get_error_message(ERROR_FORBIDDEN)

    def _get_error_message(self, error_code: int) -> bytes:
        """
        Формирование сообщения об ошибке.

        :param error_code: код ошибки
        :return: error_message - сообщение об ошибке
        """
        error_descr = self.HTTP_CODES[error_code]
        date = datetime.now().ctime()
        error_message = (
            f"HTTP/1.1 {error_code} {error_descr}\r\n"
            f"Date: {date}\r\n"
            f"Server: Python 3.10\r\n"
            f"Connection: Closed\r\n\r\n"
        )
        logging.error("Response error status: %s", str(error_code))
        return str.encode(error_message)
