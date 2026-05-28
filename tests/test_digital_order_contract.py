import unittest

from iqoptionapi.api import nested_dict
from iqoptionapi.stable_api import IQ_Option


class TestDigitalOrderContract(unittest.TestCase):
    def test_buy_digital_times_out_with_sleep_and_diagnostics(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            digital_option_placed_id = None

            def place_digital_option(self, instrument_id, amount):
                del instrument_id, amount

        api.api = _FakeApi()

        self.assertEqual(api.buy_digital(1, "instrument", timeout=0.01), (False, None))
        self.assertEqual(api.last_operation["name"], "buy_digital")
        self.assertEqual(api.last_operation["status"], "timeout")

    def test_buy_digital_records_success(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            digital_option_placed_id = None

            def place_digital_option(self, instrument_id, amount):
                del instrument_id, amount
                self.digital_option_placed_id = 9001

        api.api = _FakeApi()

        self.assertEqual(api.buy_digital(1, "instrument", timeout=1), (True, 9001))
        self.assertEqual(api.last_operation["name"], "buy_digital")
        self.assertEqual(api.last_operation["status"], "ok")
        self.assertEqual(api.last_operation["payload"]["id"], 9001)

    def test_buy_digital_spot_rejects_invalid_action(self):
        api = IQ_Option("email", "password")

        self.assertEqual(api.buy_digital_spot("EURUSD", 1, "bad", 1, timeout=0.01), -1)
        self.assertEqual(api.last_operation["name"], "buy_digital_spot")
        self.assertEqual(api.last_operation["reason"], "invalid_action")

    def test_close_digital_option_times_out_waiting_for_position(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            result = None
            order_async = nested_dict(2, dict)

        api.api = _FakeApi()

        self.assertFalse(api.close_digital_option(9001, timeout=0.01))
        self.assertEqual(api.last_operation["name"], "close_digital_option")
        self.assertEqual(api.last_operation["reason"], "position_changed_timeout")

    def test_close_digital_option_records_success(self):
        api = IQ_Option("email", "password")

        class _FakeApi:
            def __init__(self):
                self.result = None
                self.closed_external_id = None
                self.order_async = nested_dict(2, dict)
                self.order_async[9001]["position-changed"] = {
                    "msg": {"external_id": "external-9001"}
                }

            def close_digital_option(self, external_id):
                self.closed_external_id = external_id
                self.result = True

        fake = _FakeApi()
        api.api = fake

        self.assertTrue(api.close_digital_option(9001, timeout=1))
        self.assertEqual(fake.closed_external_id, "external-9001")
        self.assertEqual(api.last_operation["name"], "close_digital_option")
        self.assertEqual(api.last_operation["status"], "ok")


if __name__ == "__main__":
    unittest.main()
