"""Command execution logic for the Redis clone server."""


def simple_string(value):
    """Format a simple string response."""

    return f"+{value}\r\n".encode("utf-8")


def integer(value):
    """Format an integer response."""

    return f":{value}\r\n".encode("utf-8")


def bulk_string(value):
    """Format a bulk string response."""

    if value is None:
        return b"$-1\r\n"
    return f"${len(value)}\r\n{value}\r\n".encode("utf-8")


def error(message):
    """Format an error response."""

    return f"-ERR {message}\r\n".encode("utf-8")


def execute_command(command, args, store, save_snapshot):
    """Execute a validated command and return the response to send back to the client."""
    if command == "PING":
        return b"+PONG\r\n"

    elif command == "SET":
        key, value = args
        result = store.set(key, value)
        save_snapshot()

        return simple_string(result)

    elif command == "GET":
        key = args[0]
        value = store.get(key)

        if value is None:
            return bulk_string(None)
        else:
            return bulk_string(value)

    elif command == "DEL":
        key = args[0]
        deleted_count = store.delete(key)

        if deleted_count:
            save_snapshot()

        return integer(deleted_count)

    elif command == "EXISTS":
        key = args[0]
        exists = store.exists(key)
        return integer(exists)

    elif command == "KEYS":

        keys = store.keys()
        if not keys:
            return b"*0\r\n"
        else:
            response = f"*{len(keys)}\r\n"
            for key in keys:
                response += f"${len(key)}\r\n{key}\r\n"
            return response.encode("utf-8")

    elif command == "FLUSHALL":

        deleted_count = store.flushall()

        if deleted_count:
            save_snapshot()

        return integer(deleted_count)

    elif command == "INCR":

        key = args[0]

        try:
            new_value = store.incr(key)
            save_snapshot()
            return integer(new_value)
        except ValueError:
            return error("value is not an integer")

    elif command == "EXPIRE":
        key = args[0]

        try:
            seconds = int(args[1])
        except ValueError:
            return error("EXPIRE seconds must be an integer")

        if seconds < 0:
            return error("EXPIRE seconds must be non-negative")

        result = store.expire(key, seconds)

        if result:
            save_snapshot()
        return integer(result)

    elif command == "TTL":
        key = args[0]

        ttl_value = store.ttl(key)
        return integer(ttl_value)

    elif command == "SAVE":
        save_snapshot()
        return b"+OK\r\n"

    else:
        return b"-ERR unknown command\r\n"
