# Benchmarking Notes

## Objective

Measure basic throughput of the Redis clone under repeated single-client operations.

## Environment

- Language: Python
- Transport: TCP sockets
- Persistence: snapshot-on-write
- Commands tested: SET, GET, INCR

## Results

### Run 1 — 1000 operations

- SET: 1435.75 ops/sec
- GET: 21222.17 ops/sec
- INCR: 1488.96 ops/sec

### Run 2 — 5000 operations

- SET: 661.70 ops/sec
- GET: 20965.71 ops/sec
- INCR: 379.05 ops/sec

## Observations

- GET operations were faster than SET operations.
- Write operations were slowed by snapshot persistence on each write.
- The server remained stable during repeated command execution.
- Current implementation prioritizes simplicity over maximum throughput.

## Future Performance Improvements

- Batch snapshot writes
- Append-only logging instead of full snapshot-on-write
- More efficient RESP parsing
- Async or event-driven networking
