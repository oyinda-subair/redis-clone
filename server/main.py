"""A simple Redis clone server implemented in Python using sockets."""

import socket
import threading

from .commands import execute_command
from .config import HOST, PORT, SNAPSHOT_PATH
from .parser import parse_command
from .persistence import SnapshotManager
from .store import KeyValueStore
from .utils import validate_command

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

    buffer = ""

    try:
        while True:
            data = client_socket.recv(4096)

            if not data:
                print(f"[{thread_name}] Client disconnected: {client_address}")
                break

            buffer += data.decode("utf-8")

            while True:
                if not buffer.strip():
                    break

                command_text = None
                if buffer.startswith("*"):
                    # Split by newline to handle RESP format
                    lines = buffer.split("\n")

                    if len(lines) < 3:
                        break  # Wait for more data

                    try:
                        num_parts = int(lines[0][1:])

                    except ValueError:
                        client_socket.sendall(b"-ERR invalid RESP format\r\n")
                        buffer = ""  # Clear buffer on error
                        break

                    expected_lines = 1 + (num_parts * 2)

                    if len(lines) < expected_lines + 1:
                        break  # Wait for more data

                    command_lines = lines[:expected_lines]
                    command_text = "\r\n".join(command_lines)
                    buffer = "\r\n".join(
                        lines[expected_lines:])  # Remaining data
                else:
                    if "\n" not in buffer:
                        break  # Wait for more data

                    line, buffer = buffer.split("\n", 1)
                    command_text = line.strip().replace("\r", "")

                if not command_text:
                    continue

                print(
                    f"[{thread_name}] Received from {client_address}: {repr(command_text)}")

                command, args = parse_command(command_text)

                if command is None:
                    client_socket.sendall(b"-ERR empty command\r\n")
                    continue

                # Validate the command and its arguments before processing

                if validate_command(command, args)[0] is False:
                    client_socket.sendall(validate_command(command, args)[1])
                    continue

                # Execute the command and get the response
                response = execute_command(command, args, store, save_snapshot)

                client_socket.sendall(response)

    except ConnectionResetError:
        print(f"[{thread_name}] Client connection reset: {client_address}")
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
