# Scenario 04 TypeScript MCP client

A minimal MCP client that spawns the Python server over stdio and calls
`read_file` with a foreign `user_id`. The response differs per variant.

## Prerequisites

- Node 20+ (tested on 24.x)
- Python 3.14+ with `uv` on PATH, from the project root
- The project's `.venv` is synced (`uv sync`)

## Setup

From `clients/ts`:
