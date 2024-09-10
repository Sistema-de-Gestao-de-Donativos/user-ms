API_TITLE = "USER MS"
API_SUMMARY = "USER MS's api built with FastAPI"
API_DESCRIPTION = "API to manage users AUTH"
API_VERSION = "0.0.1"

API_CONTACT = {
    "name": "Time 2 PUCRS",
    "url": "https://github.com/",
}

API_HOST = "127.0.0.1"
API_PORT = 8000

API_ALLOWED_ORIGINS = [
    # ["http://localhost:8000"],
    "*"
]

DB_SCRIPT_MYSQL = "mysql+pymysql"
DB_SCRIPT_SQLITE = "sqlite"
ACCEPTED_DB_SCRIPTS = [DB_SCRIPT_SQLITE, DB_SCRIPT_MYSQL]

DB_URL_SQLITE = f"{DB_SCRIPT_SQLITE}:///db"
DB_URL_TEST_API = f"{DB_URL_SQLITE}/db_api.test.db"
DB_URL_TEST_E2E = f"{DB_URL_SQLITE}/db_e2e.test.db"
