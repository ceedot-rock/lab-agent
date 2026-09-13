#!/usr/bin/env python3
"""Lab agent store — check / translate / squeeze. Receipt or refuse. No 501 stubs."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8788"))
HOST = os.environ.get("HOST", "0.0.0.0")
TIMEOUT = int(os.environ.get("LAB_AGENT_TIMEOUT", "90"))
MAX_SOURCE = int(os.environ.get("LAB_AGENT_MAX_SOURCE", "200000"))
CUNI = os.environ.get("CUNI_BIN") or shutil.which("cuni") or "/usr/local/bin/cuni"
PCCX = os.environ.get("PCCX_BIN") or shutil.which("pccx") or "/usr/local/bin/pccx"
PIN_CHECK = os.environ.get("PIN_CHECK", "v0.1.10")
PIN_BANK = os.environ.get("PIN_BANK", "cuni-bank-0.1.0")
PIN_PCCX = os.environ.get("PIN_PCCX", "e72528b")


def fnv1a64(data: bytes) -> str:
    h = 0xCBF29CE484222325
    for b in data:
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{h:016x}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], timeout: int = TIMEOUT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def receipt(**kw) -> dict:
    out = {k: v for k, v in kw.items() if v is not None}
    for k in ("verb", "ok", "source_hash", "pin"):
        if k not in out:
            raise ValueError(f"receipt missing {k}")
    return out


def do_check(source: str) -> dict:
    raw = source.encode("utf-8")
    h = sha256(raw)
    with tempfile.TemporaryDirectory(prefix="lab-check-") as td:
        p = Path(td) / "n.cuni"
        p.write_text(source, encoding="utf-8")
        r = run([CUNI, "check", str(p), "--only", "py,go,js", "--timeout", "60"])
        ok = r.returncode == 0 and "exactness: PASS" in (r.stdout or "")
        return receipt(
            verb="check",
            ok=ok,
            source_hash=h,
            pin=PIN_CHECK,
            stdout=(r.stdout or "").strip(),
            refuse=None if ok else ((r.stderr or r.stdout or "check refuse").strip()),
        )


def do_translate(source: str, frm: str, to: str) -> dict:
    raw = source.encode("utf-8")
    h = fnv1a64(raw)
    frm = (frm or "py").strip().lower()
    to = (to or "js").strip().lower()
    with tempfile.TemporaryDirectory(prefix="lab-bank-") as td:
        ext = "cuni" if frm == "cuni" else "py"
        inp = Path(td) / f"n.{ext}"
        outp = Path(td) / "emit.out"
        inp.write_text(source, encoding="utf-8")
        r = run(
            [CUNI, "bank", "paste", str(inp), "--from", frm, "--to", to, "-o", str(outp)]
        )
        artifact = outp.read_text(encoding="utf-8") if outp.is_file() else ""
        ok = r.returncode == 0 and "bank: PASS" in (r.stdout or "")
        return receipt(
            verb="translate",
            ok=ok,
            source_hash=h,
            pin=PIN_BANK,
            from_lang=frm,
            to=to,
            artifact=artifact,
            summary=(r.stdout or "").strip(),
            refuse=None if ok else ((r.stderr or r.stdout or "bank refuse").strip()),
        )


def do_squeeze(data: bytes) -> dict:
    h = sha256(data)
    if not Path(PCCX).is_file():
        return receipt(
            verb="squeeze",
            ok=False,
            source_hash=h,
            pin=PIN_PCCX,
            refuse="pccx binary missing",
        )
    with tempfile.TemporaryDirectory(prefix="lab-pccx-") as td:
        inp = Path(td) / "in.bin"
        outp = Path(td) / "out.bin"
        inp.write_bytes(data)
        r = run([PCCX, "encode", str(inp), str(outp)])
        packed = outp.read_bytes() if outp.is_file() else b""
        ok = r.returncode == 0 and packed and len(packed) < len(data)
        if r.returncode == 0 and packed and len(packed) >= len(data):
            return receipt(
                verb="squeeze",
                ok=False,
                source_hash=h,
                pin=PIN_PCCX,
                refuse="never-expand: packed ≥ raw",
                raw_bytes=len(data),
                packed_bytes=len(packed),
            )
        import base64

        return receipt(
            verb="squeeze",
            ok=ok,
            source_hash=h,
            pin=PIN_PCCX,
            raw_bytes=len(data),
            packed_bytes=len(packed) if packed else 0,
            packed_b64=base64.b64encode(packed).decode("ascii") if ok else None,
            stdout=(r.stdout or "").strip(),
            refuse=None if ok else ((r.stderr or r.stdout or "pccx refuse").strip()),
        )


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    n = int(handler.headers.get("Content-Length") or "0")
    raw = handler.rfile.read(n) if n else b"{}"
    try:
        data = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise ValueError("invalid JSON")
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    return data


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: dict | bytes, ctype: str = "application/json") -> None:
        if isinstance(body, dict):
            payload = json.dumps(body).encode("utf-8")
        else:
            payload = body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/health", "/healthz"):
            return self._send(
                200,
                {
                    "ok": True,
                    "store": "slidphilabs-agent-store",
                    "verbs": ["check", "translate", "squeeze"],
                    "cuni": Path(CUNI).is_file(),
                    "pccx": Path(PCCX).is_file(),
                    "pins": {"check": PIN_CHECK, "translate": PIN_BANK, "squeeze": PIN_PCCX},
                },
            )
        if path in ("/.well-known/ai-products.json", "/ai-products.json"):
            return self._send(200, (ROOT / ".well-known" / "ai-products.json").read_bytes())
        if path in ("/mcp/tools.json", "/tools.json"):
            return self._send(200, (ROOT / "mcp" / "tools.json").read_bytes())
        if path == "/receipt.schema.json":
            return self._send(200, (ROOT / "receipt.schema.json").read_bytes())
        return self._send(404, {"ok": False, "refuse": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            data = read_json(self)
        except ValueError as e:
            return self._send(400, {"ok": False, "refuse": str(e)})
        try:
            if path == "/v1/check":
                source = data.get("source")
                if not isinstance(source, str) or not source.strip():
                    return self._send(400, receipt(verb="check", ok=False, source_hash="", pin=PIN_CHECK, refuse="missing source"))
                if len(source) > MAX_SOURCE:
                    return self._send(400, receipt(verb="check", ok=False, source_hash="", pin=PIN_CHECK, refuse="source too large"))
                rec = do_check(source)
                return self._send(200 if rec["ok"] else 422, rec)
            if path == "/v1/translate":
                source = data.get("source")
                if not isinstance(source, str) or not source.strip():
                    return self._send(400, receipt(verb="translate", ok=False, source_hash="", pin=PIN_BANK, refuse="missing source"))
                if len(source) > MAX_SOURCE:
                    return self._send(400, receipt(verb="translate", ok=False, source_hash="", pin=PIN_BANK, refuse="source too large"))
                rec = do_translate(source, str(data.get("from") or "py"), str(data.get("to") or "js"))
                return self._send(200 if rec["ok"] else 422, rec)
            if path == "/v1/squeeze":
                if data.get("data_b64"):
                    import base64

                    raw = base64.b64decode(str(data["data_b64"]))
                elif isinstance(data.get("source"), str):
                    raw = data["source"].encode("utf-8")
                else:
                    return self._send(400, receipt(verb="squeeze", ok=False, source_hash="", pin=PIN_PCCX, refuse="missing data_b64 or source"))
                if len(raw) > MAX_SOURCE:
                    return self._send(400, receipt(verb="squeeze", ok=False, source_hash=sha256(raw), pin=PIN_PCCX, refuse="payload too large"))
                rec = do_squeeze(raw)
                return self._send(200 if rec["ok"] else 422, rec)
        except subprocess.TimeoutExpired:
            return self._send(504, {"ok": False, "refuse": f"timeout after {TIMEOUT}s"})
        except FileNotFoundError as e:
            return self._send(503, {"ok": False, "refuse": str(e)})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"ok": False, "refuse": str(e)})
        return self._send(404, {"ok": False, "refuse": "not found"})


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"lab-agent store → http://{HOST}:{PORT}/  cuni={Path(CUNI).is_file()} pccx={Path(PCCX).is_file()}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
