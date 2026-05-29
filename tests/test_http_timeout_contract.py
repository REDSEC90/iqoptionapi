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


if __name__ == "__main__":
    unittest.main()
