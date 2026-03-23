"""server/utils.py"""


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
    elif command == "EXISTS":
        if len(args) != 1:
            return False, b"-ERR wrong number of arguments for EXISTS\r\n"
        return True, None
    else:
        return False, b"-ERR unknown command\r\n"
