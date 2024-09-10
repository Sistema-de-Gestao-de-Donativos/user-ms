from typing import TypeVar


T = TypeVar('T')


def get_by_id(list: list[T], id) -> T:
    """
    Returns the item with the given id from the given list.

    Args:
        list (list): List of items.
        id: Item id.

    Returns:
        Item with the given id or None if not found.
    """

    for item in list:
        if item.id == id:
            return item
    return None
