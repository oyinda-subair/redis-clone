# Redis Clone (Python)

A lightweight Redis-like in-memory key-value store built from scratch using Python sockets. Supports TTL, persistence, RESP parsing, transactions, and benchmarking.

## Features

- TCP server using raw sockets
- Key-value store with thread-safe access
- TTL expiration (`EXPIRE`, `TTL`)
- Snapshot persistence to disk
- Basic RESP protocol support
- Transactions (`MULTI`, `EXEC`, `DISCARD`)
- Benchmarking tools
- Dockerized for easy deployment

## Architecture

The system is organized into modular components:

- `main.py` — TCP server and client connection handling
- `commands.py` — command execution logic
- `store.py` — in-memory data store with TTL support
- `persistence.py` — snapshot save/load logic
- `parser.py` — command parsing (plain text + RESP)
- `config.py` — runtime configuration

## Run Locally

```bash
python3 server/main.py

nc 127.0.0.1 6379
```

---

## How to Run (Docker)

## Run with Docker

```bash
docker build -t redis-clone .
docker run --rm -p 6379:6379 -v "$(pwd)/data:/app/data" redis-clone
```

---

## Example Commands

```markdown
## Example Commands

PING
SET name Alice
GET name
INCR counter
EXPIRE name 10
TTL name

MULTI
SET a 1
SET b 2
EXEC
```

## Benchmark Results (1000 Operations)

| Command | Ops/sec  |
| ------- | -------- |
| SET     | 1435.75  |
| GET     | 21222.17 |
| INCR    | 1488.96  |

### Observations

- GET operations were faster than SET operations
- Write performance is impacted by snapshot persistence
- System remains stable under repeated load

## Future Improvements

- Append-only file (AOF) persistence
- Full RESP protocol compliance
- Async/event-driven networking
- Improved memory efficiency
- Replication support

## Quick Demo

```bash
nc 127.0.0.1 6379
```

The run:

```bash
SET hello world
GET hello

```

Simple, but effective.

---

# 7. Final polish checklist

Make sure:

- README is clean and readable
- commands all work
- Docker works
- benchmark numbers are included
- docs folder exists and is useful
- repo looks professional

---

# What you just accomplished

You built a system that includes:

- networking (TCP server)
- protocol parsing
- in-memory data structures
- TTL logic
- persistence
- transactions
- benchmarking
- containerization

That is **way above average** for a self-driven project.

---

# If you want next projects (after this)

Now that you’ve completed this, strong next options would be:

1. **Distributed version of this (leader + replicas)**
2. **Async version using `asyncio`**
3. **API gateway / reverse proxy**
4. **Real-time system (WebSockets + pub/sub)**

But don’t rush yet—this one is already a solid portfolio piece.

---

# Final step

Commit your final version:

```bash
git add .
git commit -m "Finalize Redis clone project with docs, benchmarks, and Docker support"
git push
```
