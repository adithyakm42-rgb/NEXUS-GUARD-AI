
import unittest
from privacy_engine import filter_payload


class TestPrivacyEngine(unittest.TestCase):

    def test_allowed_fields(self):
        data = {
            "cpu_usage": 25.0,
            "memory_usage": 80.0,
            "password": "secret123"
        }

        approved, blocked = filter_payload(data)

        self.assertIn("cpu_usage", approved)
        self.assertIn("memory_usage", approved)
        self.assertNotIn("password", approved)

    def test_password_blocked(self):
        data = {"password": "secret123"}

        approved, blocked = filter_payload(data)

        self.assertNotIn("password", approved)
        self.assertIn("password", blocked)

    def test_token_blocked(self):
        data = {"access_token": "abc123"}

        approved, blocked = filter_payload(data)

        self.assertNotIn("access_token", approved)
        self.assertIn("access_token", blocked)

    def test_raw_logs_blocked(self):
        data = {"raw_log": "Sensitive internal log"}

        approved, blocked = filter_payload(data)

        self.assertNotIn("raw_log", approved)
        self.assertIn("raw_log", blocked)

    def test_unexpected_fields_blocked(self):
        data = {"unknown_field": "unexpected data"}

        approved, blocked = filter_payload(data)

        self.assertEqual(approved, {})
        self.assertIn("unknown_field", blocked)


if __name__ == "__main__":
    unittest.main(verbosity=2)
