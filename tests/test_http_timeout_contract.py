import unittest

from iqoptionapi.api import IQOptionAPI


class _Resource:
    url = "resource"


class _Response:
    text = "{}"
    headers = {}
    cookies = {}

    def raise_for_status(self):
        return None


class _Session:
    def __init__(self):
        self.calls = []
        self.headers = {}
        self.cookies = _Cookies()
        self.verify = True
        self.trust_env = True

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return _Response()


class _Cookies:
    def get_dict(self):
        return {}


class _FailingSession(_Session):
    def request(self, **kwargs):
        self.calls.append(kwargs)
        raise TimeoutError("network stalled")


class TestHttpTimeoutContract(unittest.TestCase):
    def test_send_http_request_uses_default_timeout(self):
        api = IQOptionAPI("iqoption.com", "email", "password")
        api.session = _Session()

        api.send_http_request(_Resource(), "GET")

        self.assertEqual(api.session.calls[0]["timeout"], 30)

    def test_send_http_request_uses_configured_timeout(self):
        api = IQOptionAPI("iqoption.com", "email", "password", request_timeout=7.5)
        api.session = _Session()

        api.send_http_request(_Resource(), "POST", data={"a": 1})

        self.assertEqual(api.session.calls[0]["timeout"], 7.5)

    def test_send_http_request_v2_uses_configured_timeout(self):
        api = IQOptionAPI("iqoption.com", "email", "password", request_timeout=3)
        api.session = _Session()

        api.send_http_request_v2("https://example.test/api", "POST")

        self.assertEqual(api.session.calls[0]["timeout"], 3)

    def test_send_http_request_records_http_error_diagnostics(self):
        api = IQOptionAPI("iqoption.com", "email", "password", request_timeout=2)
        api.session = _FailingSession()

        with self.assertRaises(TimeoutError):
            api.send_http_request(_Resource(), "GET")

        self.assertEqual(
            api.http_last_request,
            {
                "method": "GET",
                "url": "https://iqoption.com/api/resource",
                "timeout": 2,
            },
        )
        self.assertEqual(api.http_last_error["type"], "TimeoutError")
        self.assertEqual(api.http_last_error["method"], "GET")
        self.assertEqual(api.http_last_error["url"], "https://iqoption.com/api/resource")
        self.assertEqual(api.http_last_error["timeout"], 2)

    def test_send_http_request_v2_records_http_error_diagnostics(self):
        api = IQOptionAPI("iqoption.com", "email", "password", request_timeout=4)
        api.session = _FailingSession()

        with self.assertRaises(TimeoutError):
            api.send_http_request_v2("https://auth.iqoption.com/api/v2/login", "POST")

        self.assertEqual(api.http_last_error["type"], "TimeoutError")
        self.assertEqual(api.http_last_error["method"], "POST")
        self.assertEqual(api.http_last_error["url"], "https://auth.iqoption.com/api/v2/login")
        self.assertEqual(api.http_last_error["timeout"], 4)


if __name__ == "__main__":
    unittest.main()
