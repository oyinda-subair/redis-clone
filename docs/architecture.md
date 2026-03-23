# Redis Clone Architecture

## Modules

- `main.py`: starts the TCP server and handles client connections
- `parser.py`: parses raw command text into command + args
- `commands.py`: executes supported Redis-like commands
- `store.py`: manages in-memory data, TTL, and thread safety
- `persistence.py`: saves and loads snapshot files
- `config.py`: holds runtime constants and file paths
