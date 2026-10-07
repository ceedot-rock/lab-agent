# Security Policy

lab-agent is the Slid Phi Labs agent store: three verbs (check, translate,
squeeze), a deposit flow, and an optional paywall. A bug that lets a verb
report success it did not earn, lets a tampered source pass a check, or lets a
receipt verify against the wrong input is a security issue, not a normal bug.

## Reporting a vulnerability

Please do not open a public issue for security problems.

- Email: corey@slidphilabs.com with the subject line `lab-agent security`
- Or use GitHub's private vulnerability reporting on this repository
  (Security tab, "Report a vulnerability")

Include the affected verb or endpoint, the source or input involved, steps or
inputs to reproduce, and what you expected versus what happened. Redact any
payment signatures from your report.

You can expect an acknowledgement within 3 business days. We will keep you
updated while we investigate and credit you in the changelog unless you prefer
to stay anonymous.

## In scope

- Receipt forgery: a receipt whose `source_hash` or `pin` does not match the
  actual input and binary it claims
- Check bypass: a modified or non-exact cuni output that still reports `ok`
- Pin drift: `PIN_CHECK` / `PIN_BANK` / `PIN_PCCX` not naming the binaries
  actually serving the verbs
- Deposit replay or hash confusion in `/v1/deposit`
- Unauthorized bypass of the 402 payment gate when enabled
- `eval/bank-add.json` fixture tampering that changes verb behavior

## Out of scope

- Deployments we do not run (the live Fly app's host config, TLS, WAF)
- Social engineering, spam, or denial-of-service against hosted demos
