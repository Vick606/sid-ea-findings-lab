# Scenario 04 TypeScript MCP client

A minimal MCP client that spawns the Python server over stdio and calls
`read_file` with a foreign `user_id`. The response differs per variant.

## Prerequisites

- Node 20+ (tested on 24.x)
- Python 3.14+ with `uv` on PATH, from the project root
- The project's `.venv` is synced (`uv sync`)
- pnpm (or npm; substitute accordingly)

## Setup

From `clients/ts`:

```
pnpm install
pnpm run build
```

## Run

```
pnpm run vulnerable
pnpm run fixed
pnpm run negative
```

## Expected output

`vulnerable`:

```
[vulnerable] tools: read_file
[vulnerable] read_file(user_id=noor, path=comp.md):
  noor: confidential compensation review
```

`fixed`:

```
[fixed] tools: read_file
[fixed] read_file(user_id=noor, path=comp.md):
  1 validation error for call[read_file]
user_id
  Unexpected keyword argument [type=unexpected_keyword_argument, input_value='noor', input_type=str]
```

The fixed tool's schema has no `user_id` parameter. The client still
sends `user_id=noor` because it is the same agent in every variant.
The MCP server rejects the call at the schema boundary. The defense is
structural: there is no argument by which a caller can select another
user's root.

`negative`:

```
[negative] tools: read_file
[negative] read_file(user_id=noor, path=comp.md):
  not found: user=noor path=comp.md
```

The agent sends the same call in all three cases. Only the server's
behavior differs. That is the point.

## Why this file exists

The corpus is Python-first. This client demonstrates that the
vulnerability and its fix are observable through the MCP protocol from
any language. The confused-deputy pattern is a property of the tool
contract, not the Python implementation.
