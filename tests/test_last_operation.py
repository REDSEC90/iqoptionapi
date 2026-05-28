import unittest

import iqoptionapi.global_value as global_value
from iqoptionapi.stable_api import IQ_Option
from iqoptionapi.ws.objects.candles import Candles


class TestLastOperation(unittest.TestCase):
    def setUp(self):
        global_value.check_websocket_if_connect = 1

    def test_get_candles_records_rejected_input(self):
        api = IQ_Option("email", "password")

        self.assertEqual(api.get_candles("MISSING", 60, 1, 999, timeout=1), [])

        self.assertEqual(api.last_operation["name"], "get_candles")
        self.assertEqual(api.last_operation["status"], "rejected")
        self.assertEqual(api.last_operation["reason"], "invalid_active")

    def test_get_candles_records_success(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            def __init__(self):
                self.candles = Candles()

            def getcandles(self, active_id, interval, count, endtime):
                del active_id, interval, count, endtime
                self.candles.candles_data = [{"from": 1, "open": 1.0, "close": 1.1}]

        api.api = _FakeApi()

        self.assertEqual(len(api.get_candles("EURUSD-OTC", 60, 1, 999, timeout=1)), 1)

        self.assertEqual(api.last_operation["name"], "get_candles")
        self.assertEqual(api.last_operation["status"], "ok")
        self.assertEqual(api.last_operation["payload"]["count"], 1)

    def test_check_win_v4_records_pending_timeout(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            socket_option_closed = {}
            order_async = {}

        api.api = _FakeApi()

        self.assertEqual(api.check_win_v4(999, timeout=0.01), (False, None))

        self.assertEqual(api.last_operation["name"], "check_win_v4")
        self.assertEqual(api.last_operation["status"], "pending")
        self.assertEqual(api.last_operation["reason"], "timeout")


if __name__ == "__main__":
    unittest.main()
