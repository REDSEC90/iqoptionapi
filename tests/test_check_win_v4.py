import unittest

from iqoptionapi.stable_api import IQ_Option


class TestCheckWinV4(unittest.TestCase):

    def test_check_win_v4_timeout_and_settled_results(self):
        api = IQ_Option("email", "password")

        class _FakeSocket:
            socket_option_closed = {
                1001: {"msg": {"win": "equal", "sum": "12.50", "win_amount": "12.50"}},
                1002: {"msg": {"win": "win", "sum": "8.00", "win_amount": "18.00"}},
                1003: {"msg": {"win": "loose", "sum": "5.00", "win_amount": "0"}},
            }

        api.api = _FakeSocket()

        self.assertEqual(api.check_win_v4(1001, timeout=1), (True, 0.0))
        self.assertEqual(api.check_win_v4(1002, timeout=1), (True, 10.0))
        self.assertEqual(api.check_win_v4(1003, timeout=1), (True, -5.0))

    def test_check_win_v4_pending_then_timeout(self):
        api = IQ_Option("email", "password")

        class _FakeSocket:
            socket_option_closed = {}

        api.api = _FakeSocket()
        self.assertEqual(api.check_win_v4(9999, timeout=1), (False, None))
