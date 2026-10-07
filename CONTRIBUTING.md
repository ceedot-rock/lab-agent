# Contributing to lab-agent

Thanks for helping keep the agent store honest: three verbs, one catalog, receipt or refuse.

## Ground rules

- **Receipt or refuse. No 501 stubs.** Every verb returns a receipt with
  `verb`, `ok`, `source_hash`, `pin` — or refuses with a reason. Never add a
  stub that claims to work.
- **Receipts must verify.** `receipt()` enforces the required keys; a refusal
  is not a retry (callers set `retry: true` only on 5xx).
- **Pin what you ship.** `PIN_CHECK`, `PIN_BANK`, and `PIN_PCCX` in `server.py`
  must name the exact cuni / cuni-bank / pccx builds the verbs ran against.
  Update the pins in the same PR that changes a binary.
- **No secret money moves.** This repo takes no payments itself; payment policy
  (402, deposits) is configuration, not code. Keep credentials out of the repo.
- Keep the public catalog (`/.well-known/ai-products.json`) and the MCP tool
  list (`/mcp/tools.json`) in sync with what `server.py` actually serves.

## Quick checks (no compiler needed)

```sh
python3 -m unittest discover -s tests   # full test suite
```

CI runs the suite plus an API smoke test (boot `server.py`, hit `/`, the
catalog, the tool list, and `receipt.schema.json`) on every pull request.

## Adding or changing a verb

1. Add or edit the handler in `server.py`.
2. Extend `tests/test_lab20.py` — at minimum one success receipt and one
   refusal case, asserting the receipt carries `verb`, `ok`, `source_hash`,
   `pin`.
3. If the verb leans on a new binary build, update the matching PIN constant.
4. Run the tests, then open a pull request using the template.

## Versioning

Releases are tagged `vX.Y.Z` (annotated tags) from `main` after the CI on the
release commit is green. There is no version constant in the tree; the tag is
the version source. Currently no release tags exist yet.
