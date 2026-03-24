"""client-tests/test_resp.py"""

import socket


HOST = "127.0.0.1"
PORT = 6379


def send_resp_command(parts):
    """
    Send a command in RESP format to the Redis clone server
    and print the response.
    """
    message = f"*{len(parts)}\n"
    for part in parts:
        message += f"${len(part)}\n{part}\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        welcome = sock.recv(1024).decode("utf-8")
        print("WELCOME:", repr(welcome))

        sock.sendall(message.encode("utf-8"))
        response = sock.recv(4096).decode("utf-8")
        print("RESPONSE:", repr(response))


if __name__ == "__main__":
    print("---- RESP PING ----")
    send_resp_command(["PING"])

    print("\n---- RESP SET ----")
    send_resp_command(["SET", "name", "Alice"])

    print("\n---- RESP GET ----")
    send_resp_command(["GET", "name"])
