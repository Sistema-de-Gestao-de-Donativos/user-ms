from pymongo import MongoClient
from pymongo.collection import Collection

from users_ms.settings import Settings

settings = Settings()


def get_collection(collection_name: str) -> Collection:
    client = MongoClient(settings.MONGO_DB_URL)
    db = client[settings.MONGO_DB_NAME]
    return db[collection_name]


def validate_cpf(cpf: str) -> str:
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        raise ValueError("CPF must be 11 digits long")

    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        raise ValueError("Invalid CPF")

    # Validate first digit
    sum_first = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = (sum_first * 10 % 11) % 10
    if first_digit != int(cpf[9]):
        raise ValueError("Invalid CPF")

    # Validate second digit
    sum_second = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = (sum_second * 10 % 11) % 10
    if second_digit != int(cpf[10]):
        raise ValueError("Invalid CPF")

    return cpf
