import http.client as httplib
import unittest


class HttpServer(unittest.TestCase):
    host = "localhost"
    port = 9000

    def setUp(self):
        self.conn = httplib.HTTPConnection(self.host, self.port, timeout=10)

    def tearDown(self):
        self.conn.close()

    def test_server_header(self):
        """Server header exists"""
        self.conn.request("GET", "/httptest/")
        r = self.conn.getresponse()
        server = r.getheader("Server")
        self.assertIsNotNone(server)

    def test_index_not_found(self):
        """directory index file absent"""
        self.conn.request("GET", "/httptest/dir1/")
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 404)

    def test_file_not_found(self):
        """absent file returns 404"""
        self.conn.request("GET", "/httptest/smdklcdsmvdfjnvdfjvdfvdfvdsfssdmfdsdfsd.html")
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 404)

    def test_file_with_slash(self):
        """slash after filename"""
        self.conn.request("GET", "/httptest/dir2/page.html/")
        r = self.conn.getresponse()
        self.assertEqual(int(r.status), 404)


loader = unittest.TestLoader()
suite = unittest.TestSuite()
a = loader.loadTestsFromTestCase(HttpServer)
suite.addTest(a)


class NewResult(unittest.TextTestResult):
    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        return doc_first_line or ""


class NewRunner(unittest.TextTestRunner):
    resultclass = NewResult


runner = NewRunner(verbosity=2)
runner.run(suite)
