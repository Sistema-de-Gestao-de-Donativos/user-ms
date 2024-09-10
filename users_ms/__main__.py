import pathlib
import sys

import uvicorn
from pydantic import ValidationError

from .settings import Settings


def main():
    sets = Settings()  # type: ignore

    uvicorn.run(
        "users_ms:create_app",
        factory=True,
        reload=sets.RELOAD,
        host=sets.HOST,
        port=sets.PORT,
        workers=sets.WORKERS,
    )


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        directory = pathlib.Path(".").absolute()
        print(
            f"The .env file is invalid or could not be "
            f"found on the current directory={directory}.\nValidation: {e}",
            file=sys.stderr,
        )
