from typing import Literal
from sqlalchemy.orm.query import Query


def printC(color: Literal["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"], text: str):
    """
        Prints a string with a given color

        :param color: The color to be used
        :param text: The text to be printed
    """
    colors = {
        "RED": 1,
        "GREEN": 2,
        "YELLOW": 3,
        "BLUE": 4,
        "MAGENTA": 5,
        "CYAN": 6,
        "WHITE": 7
    }
    colorCode = colors.get(color)
    print(f"\033[3{colorCode}m", text, "\033[0m")


def printI(text: str, level: int, increment: int = 4):
    """
        Prints a string indented by a given level

        :param level: The indentation level
        :param text: The text to be printed
    """
    indentation = level * increment
    print(" " * indentation, text)


def printList(list: list):
    """
        Prints a list of items

        :param list: The list to be printed
    """
    for item in list:
        index = list.index(item) + 1
        print(f'   ({index})', item)


def printQuery(query: Query):
    """
        Prints a query

        :param query: The query to be printed
    """
    printC("CYAN", "Query:")
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))
