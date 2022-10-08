# stdlib
import email
import mimetypes
import os
from datetime import datetime
from io import StringIO

CODE_200 = 200
ERROR_403 = 403
ERROR_404 = 404
ERROR_405 = 405


class Request:
    ENABLED_METHODS = ["GET", "HEAD"]
    ENABLED_FORMATS = ["html", "css", "js", "jpg", "jpeg", "png", "gif", "swf"]
    HTTP_ERRORS = {ERROR_403: "Forbidden", ERROR_404: "Not Found", ERROR_405: "Method Not Allowed"}
    HTTP_CODES = {CODE_200: "OK"}

    def __init__(self, request_bytes: bytes, document_root):
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
        method, req_body, http_ver = request.split(" ")
        message = email.message_from_file(StringIO(headers))
        headers = dict(message.items())
        parsed_request_data = {"method": method, "body": req_body, "ver": http_ver, "headers": headers}
        return parsed_request_data

    def _form_response(self, req_data: dict) -> bytes:
        """
        Формирование ответа на запрос.

        :param req_data: извлеченные из запроса данные
        :return: response - сформированный ответ
        """
        if req_data["method"] not in self.ENABLED_METHODS:
            return self._get_error_message(ERROR_405)

        path = self.document_root + req_data["body"]
        if not os.path.exists(path):
            return self._get_error_message(ERROR_404)

        if os.path.isdir(path) and "index.html" in os.listdir(path):
            return self._get_message(req_data["method"], path + "index.html", ".html")

        if os.path.isfile(path):
            name, extension = os.path.splitext(path)
            return self._get_message(req_data["method"], path, extension)

        return self._get_error_message(ERROR_404)

    def _get_message(self, method: str, filepath: str, extension: str) -> bytes:
        try:
            with open(filepath, "rb") as f:
                content = f.read()
                content_len = len(content)
                content_type = mimetypes.types_map[extension]
                date = datetime.now().ctime()
                message = (
                    f"HTTP/1.1 {CODE_200} {self.HTTP_CODES[CODE_200]}\r\n"
                    f"Date: {date}\r\n"
                    f"Server: Python 3.10\r\n"
                    f"Content-Length: {content_len}\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Connection: Closed\r\n\r\n"
                )
                message = str.encode(message)
                if method == "GET":
                    message += content
                return message
        except Exception:
            return self._get_error_message(ERROR_403)

    def _get_error_message(self, error_code: int) -> bytes:
        """
        Формирование сообщения об ошибке.

        :param error_code: код ошибки
        :return: error_message - сообщение об ошибке
        """
        error_descr = self.HTTP_ERRORS[error_code]
        date = datetime.now().ctime()
        error_message = (
            f"HTTP/1.1 {error_code} {error_descr}\r\n"
            f"Date: {date}\r\n"
            f"Server: Python 3.10\r\n"
            f"Connection: Closed\r\n\r\n"
        )

        return str.encode(error_message)
