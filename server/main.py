"""A simple Redis clone server implemented in Python using sockets."""

import os
import socket
import threading

from .parser import parse_command
from .persistence import SnapshotManager
from .store import KeyValueStore
from .utils import validate_command

HOST = "127.0.0.1"
PORT = 6379

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_PATH = os.path.join(BASE_DIR, "..", "data", "snapshot.json")

# Initialize the Redis store
store = KeyValueStore()
# Load existing data from snapshot if available
snapshot_manager = SnapshotManager(SNAPSHOT_PATH)


def save_snapshot():
    """Save the current state of the key-value store to a snapshot file."""
    data, expiry = store.export_snapshot()
    snapshot_manager.save(data, expiry)
    print(f"Snapshot saved with {len(data)} keys")


def load_snapshot():
    """Load the key-value store state from a snapshot file."""
    data, expiry = snapshot_manager.load()
    store.load_snapshot(data, expiry)
    print(f"Loaded snapshot with {len(data)} keys")

# Function to handle client connections and respond to commands.


def handle_client(client_socket, client_address):
    """Handle a client connection, receive commands, and send responses."""

    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Client connected from {client_address}")
    client_socket.sendall(b"+OK\r\n")

    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                print(f"[{thread_name}] Client disconnected: {client_address}")
                break

            raw_input = data.decode("utf-8").strip()
            print(f"[{thread_name}] Received from {client_address}: {raw_input}")

            command, args = parse_command(raw_input)

            if command is None:
                client_socket.sendall(b"-ERR empty command\r\n")
                continue

            # Validate the command and its arguments before processing
            if validate_command(command, args)[0] is False:
                client_socket.sendall(validate_command(command, args)[1])
                continue

            if command == "PING":
                client_socket.sendall(b"+PONG\r\n")

            elif command == "SET":
                key, value = args
                result = store.set(key, value)
                save_snapshot()

                client_socket.sendall(
                    f"+{result}\r\n".encode("utf-8")
                )

            elif command == "GET":
                key = args[0]
                value = store.get(key)

                if value is None:
                    client_socket.sendall(b"$-1\r\n")
                else:
                    client_socket.sendall(
                        f"${len(value)}\r\n{value}\r\n".encode(
                            "utf-8")
                    )

            elif command == "DEL":
                key = args[0]
                deleted_count = store.delete(key)

                if deleted_count:
                    save_snapshot()

                client_socket.sendall(
                    f":{deleted_count}\r\n".encode("utf-8")
                )

            elif command == "EXISTS":
                key = args[0]
                exists = store.exists(key)
                client_socket.sendall(
                    f":{exists}\r\n".encode("utf-8")
                )

            elif command == "KEYS":

                keys = store.keys()
                if not keys:
                    client_socket.sendall(b"*0\r\n")
                else:
                    response = f"*{len(keys)}\r\n"
                    for key in keys:
                        response += f"${len(key)}\r\n{key}\r\n"
                    client_socket.sendall(response.encode("utf-8"))

            elif command == "FLUSHALL":

                deleted_count = store.flushall()

                if deleted_count:
                    save_snapshot()

                client_socket.sendall(f":{deleted_count}\r\n".encode("utf-8"))

            elif command == "INCR":

                key = args[0]

                try:
                    new_value = store.incr(key)
                    save_snapshot()
                    client_socket.sendall(f":{new_value}\r\n".encode("utf-8"))
                except ValueError:
                    client_socket.sendall(b"-ERR value is not an integer\r\n")

            elif command == "EXPIRE":
                key = args[0]

                try:
                    seconds = int(args[1])
                except ValueError:
                    client_socket.sendall(
                        b"-ERR EXPIRE seconds must be an integer\r\n")
                    continue

                if seconds < 0:
                    client_socket.sendall(
                        b"-ERR EXPIRE seconds must be non-negative\r\n")
                    continue

                result = store.expire(key, seconds)

                if result:
                    save_snapshot()
                client_socket.sendall(f":{result}\r\n".encode("utf-8"))

            elif command == "TTL":
                key = args[0]

                ttl_value = store.ttl(key)
                client_socket.sendall(f":{ttl_value}\r\n".encode("utf-8"))

            elif command == "SAVE":
                if len(args) != 0:
                    client_socket.sendall(b"-ERR SAVE takes no arguments\r\n")
                    continue

                save_snapshot()
                client_socket.sendall(b"+OK\r\n")

            else:
                client_socket.sendall(b"-ERR unknown command\r\n")

    except ConnectionResetError:
        print(f"Client connection reset: {client_address}")
    finally:
        client_socket.close()

# Basic Redis clone server that accepts connections and responds to commands.


def main():
    """Create a TCP socket, bind it to the specified host and port,
    and listen for incoming connections."""

    load_snapshot()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Redis clone server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True,
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nShutting down server...")
        save_snapshot()

    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    main()
