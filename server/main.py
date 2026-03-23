"""A simple Redis clone server implemented in Python using sockets."""

import socket
from .store import KeyValueStore
from .parser import parse_command
from .utils import validate_command

HOST = "127.0.0.1"
PORT = 6379

# Initialize the Redis store
store = KeyValueStore()

# Function to handle client connections and respond to commands.


def handle_client(client_socket, client_address):
    """Handle a client connection, receive commands, and send responses."""
    print(f"Client connected from {client_address}")
    client_socket.sendall(b"+OK\r\n")

    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                print(f"Client disconnected: {client_address}")
                break

            raw_input = data.decode("utf-8").strip()
            print(f"Received from {client_address}: {raw_input}")

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
                client_socket.sendall(f":{deleted_count}\r\n".encode("utf-8"))

            elif command == "INCR":

                key = args[0]

                try:
                    new_value = store.incr(key)
                    client_socket.sendall(f":{new_value}\r\n".encode("utf-8"))
                except ValueError:
                    client_socket.sendall(b"-ERR value is not an integer\r\n")
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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Redis clone server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address)

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    main()
