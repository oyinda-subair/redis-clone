import socket


HOST = "127.0.0.1"
PORT = 6379


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Redis clone server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Client connected from {client_address}")

            client_socket.sendall(b"+OK Connected to Redis clone\r\n")
            client_socket.close()

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    main()
