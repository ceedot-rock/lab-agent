# Lab status

Updated 2026-09-14.

## Public nouns

check · translate · squeeze

## Pins

| verb | pin | live |
|---|---|---|
| check | cuni v0.1.10 / Bank tag cuni-bank-0.1.0 | POST https://spl-lab-agent.fly.dev/v1/check |
| translate | cuni-bank-0.1.0 | POST https://spl-lab-agent.fly.dev/v1/translate |
| squeeze | pccx e72528b (0.3.0 tree) | POST https://spl-lab-agent.fly.dev/v1/squeeze |

Health: https://spl-lab-agent.fly.dev/healthz
Catalog: https://spl-lab-agent.fly.dev/.well-known/ai-products.json

## Measured 2026-09-13

- check `say(1)` → ok, exactness PASS (3 langs)
- translate py→js `print(1)` → bank PASS
- squeeze 84B → packed 76 DECODE_OK

## Law

119 languages = `cuni check` after ingest. Bank ingest is Python subset or `.cuni`.
Close GitHub issues only with a URL + receipt in the comment.

## Pay

https://www.slidphilabs.com/api/agent — not yet a per-verb meter on Fly.
