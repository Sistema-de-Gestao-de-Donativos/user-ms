from os import environ as env
from dotenv import load_dotenv


def validate_env(required_variables: dict[str, str], invalid_values: list = [None]) -> None:
    """
    Function to validate the environment variables.

    Args:
        required_variables (dict[str, str]): The required environment variables.

    Raises:
        ValueError: If any of the required environment variables is missing.
    """
    for key, value in required_variables.items():
        if value in invalid_values:
            raise ValueError(
                f"Missing environment variable: '{key}'. Invalid value: '{value}'.")


def get_jwt_env():
    """
    Function to get the JWT related environment variables.

    Raises:
        ValueError: If any of the required environment variables is missing.

    Returns:
        dict: The JWT secret, algorithm and access token expire minutes.
    """
    from schemas.Access_Logs import ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT, REFRESH_TOKEN_EXPIRE_MINUTES_DEFAULT
    load_dotenv()

    JWT_SECRET = env.get("JWT_SECRET")
    ALGORITHM = env.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(env.get("ACCESS_TOKEN_EXPIRE_MINUTES",
                                              ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(env.get("REFRESH_TOKEN_EXPIRE_MINUTES",
                                               REFRESH_TOKEN_EXPIRE_MINUTES_DEFAULT))

    required_variables = {
        "JWT Secret": JWT_SECRET,
        "Algorithm": ALGORITHM,
        "Access Token Expire Minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "Refresh Token Expire Minutes": REFRESH_TOKEN_EXPIRE_MINUTES,
    }

    validate_env(required_variables)

    return required_variables


def get_db_env():
    """
    Function to get and validate the database environment variables.

    Raises:
        ValueError: If any of the required environment variables is missing.

    Returns:
        tuple: The database script and URL.
    """
    from sqlalchemy.engine.url import URL
    from utils.config import ACCEPTED_DB_SCRIPTS, DB_SCRIPT_SQLITE, DB_URL_SQLITE
    load_dotenv()

    DB_SCRIPT = env.get("DB_SCRIPT") or DB_SCRIPT_SQLITE
    DB_USER = env.get("DB_USER")
    DB_PASSWORD = env.get("DB_PASSWORD")
    DB_HOST = env.get("DB_HOST")
    DB_PORT = env.get("DB_PORT")
    DB_NAME = env.get("DB_NAME") or "autogenerated_empty.env"

    if DB_SCRIPT not in ACCEPTED_DB_SCRIPTS:
        raise ValueError(
            f"Invalid database script: '{DB_SCRIPT}'. Should be one of {ACCEPTED_DB_SCRIPTS}.")
    elif DB_SCRIPT == DB_SCRIPT_SQLITE:
        DB_URL = f"{DB_URL_SQLITE}/{DB_NAME}.sqlite"
    else:
        required_fields = {
            "DB_SCRIPT": DB_SCRIPT,
            "DB_USER": DB_USER,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_NAME": DB_NAME,
        }
        validate_env(required_fields, invalid_values=[""])
        try:
            DB_URL = URL.create(
                drivername=DB_SCRIPT,
                username=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
            )
        except Exception:
            DB_URL = f"{DB_SCRIPT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    required_variables = {
        "Script": DB_SCRIPT,
        "URL": DB_URL,
    }

    return required_variables


def get_control_panel_env():
    """
    Function to get and validate the control panel environment variables.

    Raises:
        ValueError: If any of the required environment variables is missing.

    Returns:
        tuple: The control panel username and password.
    """
    load_dotenv()

    CONTROL_PANEL_URL = env.get("CONTROL_PANEL_URL")
    CP_RESET_PASSWORD_ENDPOINT = env.get("CP_RESET_PASSWORD_ENDPOINT")

    required_variables = {
        "URL": CONTROL_PANEL_URL,
        "Reset Password Endpoint": CP_RESET_PASSWORD_ENDPOINT,
    }

    validate_env(required_variables)

    return required_variables


def get_email_env():
    """
    Function to get and validate the e-mail environment variables.

    Raises:
        ValueError: If any of the required environment variables is missing.

    Returns:
        tuple: The e-mail server, port, address and secret.
    """
    load_dotenv()

    EMAIL_SERVER = env.get("EMAIL_SERVER")
    EMAIL_PORT = env.get("EMAIL_PORT")
    EMAIL_ADDRESS = env.get("EMAIL_ADDRESS")
    EMAIL_SECRET = env.get("EMAIL_SECRET")

    required_variables = {
        "Server": EMAIL_SERVER,
        "Port": EMAIL_PORT,
        "Address": EMAIL_ADDRESS,
        "Secret": EMAIL_SECRET,
    }

    validate_env(required_variables)

    return required_variables
