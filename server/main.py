import socket


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

            command = data.decode("utf-8").strip()
            print(f"Received from {client_address}: {command}")

            if command.upper() == "PING":
                client_socket.sendall(b"+PONG\r\n")
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
