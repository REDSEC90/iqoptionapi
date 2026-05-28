import unittest

from iqoptionapi.api import IQOptionAPI


class TestInstanceState(unittest.TestCase):
    def test_instances_do_not_share_closed_option_state(self):
        first = IQOptionAPI("iqoption.com", "first@example.test", "password")
        second = IQOptionAPI("iqoption.com", "second@example.test", "password")

        payload = {"msg": {"option_id": 1001, "profit_amount": "18", "amount": "8"}}
        first.socket_option_closed[1001] = payload
        first.order_async[1001]["option-closed"] = payload

        self.assertEqual(second.socket_option_closed, {})
        self.assertEqual(second.order_async[1001], {})

    def test_instances_do_not_share_candles_or_realtime_cache(self):
        first = IQOptionAPI("iqoption.com", "first@example.test", "password")
        second = IQOptionAPI("iqoption.com", "second@example.test", "password")

        first.candles.candles_data = [{"from": 1, "open": 1.0, "close": 1.1}]
        first.real_time_candles["EURUSD-OTC"][60][1] = {"from": 1}

        self.assertIsNone(second.candles.candles_data)
        self.assertEqual(second.real_time_candles["EURUSD-OTC"][60], {})


if __name__ == "__main__":
    unittest.main()
