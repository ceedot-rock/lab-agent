"""LAB20 #7 #8 #16 #18 — deposit hash, no retry on refuse, optional 402."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Deposit(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        os.environ["LAB_DEPOSIT_DIR"] = self.td
        os.environ["LAB_REQUIRE_PAY"] = "0"
        import server

        importlib.reload(server)
        self.s = server

    def test_refuse_without_hash(self):
        blob = b"hello lab20"
        rec = self.s.deposit_put("", blob)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["source_hash"], sha(blob))
        self.assertFalse(rec["retry"])
        self.assertIn("new object", rec["refuse"])

    def test_refuse_mismatch(self):
        blob = b"hello lab20"
        rec = self.s.deposit_put("deadbeef", blob)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["source_hash"], sha(blob))
        self.assertFalse(rec["retry"])

    def test_put_get(self):
        blob = b"hello lab20"
        h = sha(blob)
        rec = self.s.deposit_put(h, blob)
        self.assertTrue(rec["ok"])
        got = self.s.deposit_get(h)
        self.assertTrue(got["ok"])
        import base64

        self.assertEqual(base64.b64decode(got["data_b64"]), blob)


class Pay402(unittest.TestCase):
    def test_402_without_signature(self):
        os.environ["LAB_REQUIRE_PAY"] = "1"
        os.environ["LAB_DEPOSIT_DIR"] = tempfile.mkdtemp()
        import server

        importlib.reload(server)
        httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        time.sleep(0.05)
        port = httpd.server_address[1]
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/check",
            data=json.dumps({"source": "say(1)"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=5)
            self.fail("expected 402")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 402)
            body = json.loads(e.read())
            self.assertEqual(body["refuse"], "payment required")
            self.assertFalse(body["retry"])
            self.assertTrue(body.get("pay"))
        finally:
            httpd.shutdown()


if __name__ == "__main__":
    unittest.main()
