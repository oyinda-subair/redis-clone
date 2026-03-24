"""A simple Redis clone server implemented in Python using sockets."""


def parse_plain_text(raw_input):
    """
    Parse a plain text command into:
    - command name
    - list of arguments
    """
    if not raw_input or not raw_input.strip():
        return None, []

    parts = raw_input.strip().split()

    if not parts:
        return None, []

    command = parts[0].upper()
    args = parts[1:]

    return command, args


def parse_resp(raw_input):
    """
    Parse a minimal RESP array format.

    Example:
    *3
    $3
    SET
    $4
    name
    $5
    Alice

    Returns:
    ("SET", ["name", "Alice"])
    """
    lines = raw_input.split("\r\n")

    if not lines or not lines[0].startswith("*"):
        return None, []

    try:
        num_parts = int(lines[0][1:])
    except ValueError:
        return None, []

    tokens = []
    index = 1

    while index < len(lines):
        line = lines[index]

        if not line:
            index += 1
            continue

        if line.startswith("$"):
            index += 1
            if index < len(lines):
                tokens.append(lines[index])
        index += 1

    if len(tokens) != num_parts or not tokens:
        return None, []

    command = tokens[0].upper()
    args = tokens[1:]
    return command, args


def parse_command(raw_input):
    """
    Parse the raw input from the client and determine the
    command and its arguments.
    Supports both plain text and RESP formats.
        - If the input starts with "*", it is treated as RESP.
        - Otherwise, it is treated as plain text.
        Returns:
            (command, args) where command is the command name
            (e.g., "SET") and args is a list of arguments.
    """
    if not raw_input:
        return None, []

    raw_input = raw_input.strip()

    if not raw_input:
        return None, []

    if raw_input.startswith("*"):
        command, args = parse_resp(raw_input)
        if command is not None:
            return command, args

    return parse_plain_text(raw_input)
