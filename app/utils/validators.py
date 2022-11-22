"""Parse"""


def parse_handle(handle: str) -> str:
    """Ensure input for handle has an '@' symbol.

    >>> parse_handle('ShivanS')
    '@ShivanS'

    Args:
        handle (str): Unique YouTube handle.

    Returns:
        (str): Correct handle representation.
    """
    if len(handle) > 0:
        first = handle[0]
        if first != "@":
            return "@" + handle
    return handle
