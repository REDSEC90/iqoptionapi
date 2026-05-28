import unittest

from iqoptionapi.api import nested_dict
from iqoptionapi.ws.client import WebsocketClient


class TestClosedOptionStorage(unittest.TestCase):
    def test_store_closed_option_updates_async_and_compat_cache(self):
        class _FakeApi:
            order_async = nested_dict(2, dict)
            socket_option_closed = {}

        client = WebsocketClient.__new__(WebsocketClient)
        client.api = _FakeApi()

        payload = {
            "name": "option-closed",
            "msg": {
                "option_id": 4001,
                "profit_amount": "18.00",
                "amount": "8.00",
            },
        }

        client._store_closed_option(payload)

        self.assertEqual(
            client.api.order_async[4001]["option-closed"],
            payload,
        )
        self.assertEqual(client.api.socket_option_closed[4001], payload)


if __name__ == "__main__":
    unittest.main()
