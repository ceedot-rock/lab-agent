# Notes for Grok — 2026-09-14

Owner: Corey / Slid Phi Labs. Do not use Grok Bots unless he has tokens.

## Public nouns only

check · translate · squeeze

## Live

- Store: https://spl-lab-agent.fly.dev/healthz
- POST /v1/check /v1/translate /v1/squeeze — measured PASS 2026-09-13
- Studio: https://cuni-studio.fly.dev/
- Pay (not per-verb meter): https://www.slidphilabs.com/api/agent

## Repos / pins

| thing | where | pin |
|---|---|---|
| CuNi + Bank CLI | https://github.com/ceedot-rock/cuni | tag cuni-bank-0.1.0 ; Cargo 0.1.11 on master `7eedba2` |
| PCCX | https://github.com/ceedot-rock/pccx **public** | 0.3.0 tree, Fly pin e72528b, README license hero `1ace560` |
| Agent store | https://github.com/ceedot-rock/lab-agent | STATUS.md `fb41cbc` |

Install Bank:
```
cargo install --git https://github.com/ceedot-rock/cuni --tag cuni-bank-0.1.0
cuni bank paste examples/bank/add.py --from py --to c
```

## Law

- Bank ingest = Python subset or `.cuni`. 119 langs = `cuni check` after ingest. NOT 119 ingest parsers.
- PCCX dual: AGPL-3.0-or-later OR commercial. Combined GC visibility ≠ closed-product grant.
- Encode never emits packed ≥ raw. DECODE_OK or no file.
- Close issues only with a live receipt in the comment.

## Done

- `mod bank` in main.rs; 10-lang gate on add.py PASS
- CI runs `cuni bank --help` + paste py→py
- PCCX public + LICENSE/COMMERCIAL
- Press: cuni/docs/PRESS_RELEASE.md ; mailed ceedotrock@gmail.com
- Drive zip of crate: https://drive.google.com/file/d/11TBqNiMFKm-x4viH-SCgW8XvQSzEAU5J/view

## Not done (do not fake)

- `cargo publish` cuni 0.1.11 (no crates.io token in this channel)
- GitHub Release objects on pccx / lab-agent
- x402 charged on the three Fly POSTs
- OSCB board row for PCCX
- Bank from=rs/c ingest

## Do next if asked

1. `cargo publish` from a machine with crates.io login
2. Tag pccx 0.3.0 GitHub Release
3. Wire pay header on spl-lab-agent POSTs
4. Keep STATUS.md pins in sync with Fly env
