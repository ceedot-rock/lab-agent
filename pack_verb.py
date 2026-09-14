"""lab-agent pack verb. Stdlib only. Not Combined GC."""

from __future__ import annotations

import hashlib
import hmac
import json
import zlib
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from struct import pack

PP = b"PP01"
SEAL = b"SEAL"


@dataclass(frozen=True)
class Rec:
    kind: int
    ts_ms: int
    key: bytes
    val: bytes


def _pack(recs):
    out = bytearray(PP + pack("<I", len(recs)))
    for r in recs:
        out += pack("<I", r.kind & 0xFFFFFFFF)
        out += pack("<Q", r.ts_ms & 0xFFFFFFFFFFFFFFFF)
        out += pack("<I", len(r.key)) + r.key
        out += pack("<I", len(r.val)) + r.val
    return bytes(out)


def _collect(events, ts_ms):
    seen = OrderedDict()
    for key, val, hint in events:
        kind = 2 if key in seen else (hint if hint in (1, 2) else 1)
        seen[key] = Rec(kind=kind, ts_ms=ts_ms, key=key, val=val)
    return list(seen.values())


def _seal(payload, key):
    nonce = hashlib.sha256(key + payload).digest()
    mac = hmac.new(key, nonce + payload, hashlib.sha256).digest()
    return SEAL + pack("B", 1) + nonce + mac + payload


def do_pack(events, key, store, ts_ms=0):
    recs = _collect(events, ts_ms)
    packed = _pack(recs)
    compressed = zlib.compress(packed, 6)
    sealed = _seal(compressed, key)
    digest = hashlib.sha256(sealed).hexdigest()
    store.mkdir(parents=True, exist_ok=True)
    dest = store / digest
    existed = dest.is_file()
    if not existed:
        dest.write_bytes(sealed)
    est = json.dumps(
        [{"k": k.decode("utf-8", "replace"), "v": v.decode("utf-8", "replace")} for k, v, _ in events],
        separators=(",", ":"),
    ).encode()
    return {
        "verb": "pack",
        "ok": True,
        "source_hash": digest,
        "pin": "packed-pipe-0.1",
        "retry": False,
        "events_in": len(events),
        "records_out": len(recs),
        "json_est": len(est),
        "packed_bytes": len(packed),
        "compressed_bytes": len(compressed),
        "sealed_bytes": len(sealed),
        "dedup": existed,
        "engine": "zlib-face",
    }
