# Lab agent store

Three verbs. One catalog. Receipt or refuse.

| verb | product | POST |
|---|---|---|
| check | CuNi exactness | `/v1/check` |
| translate | CuNi Bank | `/v1/translate` |
| squeeze | PCCX | `/v1/squeeze` |

Discovery: `GET /.well-known/ai-products.json`
Tools: `GET /mcp/tools.json`
Eval: `eval/bank-add.json`

Pay: https://www.slidphilabs.com/api/agent

Live: https://spl-lab-agent.fly.dev/ · canonical catalog https://www.slidphilabs.com/.well-known/ai-products.json

```
POST /v1/check      { "source": "say(1)" }
POST /v1/translate  { "source": "print(1)", "from": "py", "to": "js" }
POST /v1/squeeze    { "data_b64": "..." }
```

Receipt always has `verb`, `ok`, `source_hash`, `pin`. Refuse is a string, never a 501 stub.
MCP on Rider: `cuni_check`, `bank_paste`, `pccx_encode`.
