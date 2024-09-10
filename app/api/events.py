from fastapi import Request


def startup_event(*_args):
    """Initialize the database with default data on startup"""

    from auth.env import get_db_env
    from db.init_db import init_db
    from db.session import get_db
    from sys import argv

    db = next(get_db())

    def argv_contains(*args):
        return any(arg in argv for arg in args)

    show_data = argv_contains("-s", "--show-data")
    reset_db = False
    if argv_contains("-r", "--reset"):
        reset_db = "initial"
    if argv_contains("-rt", "--reset-test"):
        reset_db = "test_set"

    db_env = get_db_env()
    db_script = db_env.get("Script")

    init_db(db, db_script=db_script,
            show_data=show_data, reset_db=reset_db)


IGNORE_LOWER_PATHS = ["/access/"]


async def case_insensitive_router(request: Request, call_next):
    """Make the router path and query params case insensitive"""
    DECODE_FORMAT = "latin-1"

    query = request.scope['query_string'].decode(DECODE_FORMAT)
    if query:
        params = query.split("&")
        key_values = [keyvalue.split("=") for keyvalue in params]
        lowerkey_values = [[keyvalue[0].lower(), keyvalue[1]]
                           for keyvalue in key_values]
        lowerkey_values = ["=".join(keyvalue) for keyvalue in lowerkey_values]
        lowerkeys_query = "&".join(lowerkey_values)
        request.scope["query_string"] = lowerkeys_query.encode(DECODE_FORMAT)

    path = request.scope["path"]
    if not any(path.startswith(ignore) for ignore in IGNORE_LOWER_PATHS):
        request.scope["path"] = path.lower()

    response = await call_next(request)

    return response
