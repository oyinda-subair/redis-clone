"""A simple Redis clone server implemented in Python using sockets."""


def parse_command(raw_input):
    """
    Parse a raw client command into:
    - command name
    - list of arguments

    Example:
    "SET name Alice" -> ("SET", ["name", "Alice"])
    """
    if not raw_input or not raw_input.strip():
        return None, []

    parts = raw_input.strip().split()

    if not parts:
        return None, []

    command = parts[0].upper()
    args = parts[1:]

    return command, args
