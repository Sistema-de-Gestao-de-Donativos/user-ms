from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    """
    Function to hash a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    """
    Function to verify a password.

    Args:
        password (str): The password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: Whether the password is verified.
    """

    return pwd_context.verify(password, hashed_password)
