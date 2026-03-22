"""A simple Redis clone server implemented in Python using sockets."""

import socket
from .parser import parse_command

HOST = "127.0.0.1"
PORT = 6379

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

            if validate_command(command, args)[0] is False:
                client_socket.sendall(validate_command(command, args)[1])
                continue

            if command == "PING":
                client_socket.sendall(b"+PONG\r\n")
            elif command == "SET":
                client_socket.sendall(
                    f"+PARSED SET command with args: {args}\r\n".encode(
                        "utf-8")
                )
            elif command == "GET":
                client_socket.sendall(
                    f"+PARSED GET command with args: {args}\r\n".encode(
                        "utf-8")
                )
            elif command == "DEL":
                client_socket.sendall(
                    f"+PARSED DEL command with args: {args}\r\n".encode(
                        "utf-8")
                )
            else:
                client_socket.sendall(b"-ERR unknown command\r\n")

    except ConnectionResetError:
        print(f"Client connection reset: {client_address}")
    finally:
        client_socket.close()


def validate_command(command, args):
    """Validate the command and its arguments."""
    if command == "PING":
        return True, None
    elif command == "SET":
        if len(args) != 2:
            return False, b"-ERR wrong number of arguments for SET\r\n"
        return True, None
    elif command == "GET":
        if len(args) != 1:
            return False, b"-ERR wrong number of arguments for GET\r\n"
        return True, None
    elif command == "DEL":
        if len(args) < 1:
            return False, b"-ERR wrong number of arguments for DEL\r\n"
        return True, None
    else:
        return False, b"-ERR unknown command\r\n"

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
