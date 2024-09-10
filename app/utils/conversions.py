def list_to_str(list_: list[int], separator: str = ",", allow_duplicates: bool = False):
    """Converts a list of integers to a string with a separator"""
    if not allow_duplicates:
        list_ = list(set(list_))
    str_list = [str(i) for i in list_]
    list_as_str = separator.join(str_list)
    return list_as_str


def str_to_list(string: str, separator: str = ","):
    """Converts a string with a separator to a list of integers"""
    string = string.replace(" ", "")
    str_list = string.split(separator)
    list_int = [int(i) for i in str_list]
    return list_int


def case_insensitive(str: str, trim_spaces: bool = True):
    """Return a version of the string suitable for caseless comparisons."""
    if trim_spaces:
        str = str.strip()
    return str.casefold()
