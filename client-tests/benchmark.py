"""client-tests/benchmark.py"""

import socket
import time


HOST = "127.0.0.1"
PORT = 6379
SOCKET_TIMEOUT_SECONDS = 5


def send_command(sock, command):
    """Send a command to the Redis clone server and return the response."""
    sock.sendall((command + "\n").encode("utf-8"))
    return sock.recv(4096)


def benchmark_set(num_operations):
    """Benchmark the SET command by setting multiple keys."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(SOCKET_TIMEOUT_SECONDS)
        sock.connect((HOST, PORT))

        start = time.perf_counter()

        for i in range(num_operations):
            response = send_command(sock, f"SET key{i} value{i}")
            if not response.startswith(b"+OK"):
                raise RuntimeError(f"Unexpected SET response: {response!r}")

        end = time.perf_counter()

    elapsed = end - start
    ops_per_second = num_operations / elapsed if elapsed > 0 else 0
    return elapsed, ops_per_second


def benchmark_get(num_operations):
    """Pre-populate keys for GET benchmark."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(SOCKET_TIMEOUT_SECONDS)
        sock.connect((HOST, PORT))

        start = time.perf_counter()

        for i in range(num_operations):
            response = send_command(sock, f"GET key{i}")
            if response.startswith(b"-ERR"):
                raise RuntimeError(f"Unexpected GET response: {response!r}")

        end = time.perf_counter()

    elapsed = end - start
    ops_per_second = num_operations / elapsed if elapsed > 0 else 0
    return elapsed, ops_per_second


def benchmark_incr(num_operations):
    """Benchmark the INCR command by incrementing a counter key multiple times."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(SOCKET_TIMEOUT_SECONDS)
        sock.connect((HOST, PORT))

        start = time.perf_counter()

        for _ in range(num_operations):
            response = send_command(sock, "INCR counter")
            if response.startswith(b"-ERR"):
                raise RuntimeError(f"Unexpected INCR response: {response!r}")

        end = time.perf_counter()

    elapsed = end - start
    ops_per_second = num_operations / elapsed if elapsed > 0 else 0
    return elapsed, ops_per_second


def benchmark_mixed(num_operations):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(SOCKET_TIMEOUT_SECONDS)
        sock.connect((HOST, PORT))
        # sock.recv(1024)  # welcome

        start = time.perf_counter()

        for i in range(num_operations):
            if i % 2 == 0:
                response = send_command(sock, f"SET mixed{i} value{i}")
            else:
                response = send_command(sock, f"GET mixed{i-1}")

            if response.startswith(b"-ERR"):
                raise RuntimeError(f"Unexpected mixed response: {response!r}")

        end = time.perf_counter()

    elapsed = end - start
    ops_per_second = num_operations / elapsed if elapsed > 0 else 0
    return elapsed, ops_per_second


def main():
    """Run benchmarks for SET, GET, and INCR commands."""
    num_operations = 5000

    print(f"Running benchmarks with {num_operations} operations each...\n")

    set_elapsed, set_ops = benchmark_set(num_operations)
    print("SET benchmark:")
    print(f"  Time elapsed: {set_elapsed:.4f} seconds")
    print(f"  Throughput:   {set_ops:.2f} ops/sec\n")

    get_elapsed, get_ops = benchmark_get(num_operations)
    print("GET benchmark:")
    print(f"  Time elapsed: {get_elapsed:.4f} seconds")
    print(f"  Throughput:   {get_ops:.2f} ops/sec\n")

    incr_elapsed, incr_ops = benchmark_incr(num_operations)
    print("INCR benchmark:")
    print(f"  Time elapsed: {incr_elapsed:.4f} seconds")
    print(f"  Throughput:   {incr_ops:.2f} ops/sec\n")

    mixed_elapsed, mixed_ops = benchmark_mixed(num_operations)
    print("MIXED benchmark:")
    print(f"  Time elapsed: {mixed_elapsed:.4f} seconds")
    print(f"  Throughput:   {mixed_ops:.2f} ops/sec\n")


if __name__ == "__main__":
    main()
