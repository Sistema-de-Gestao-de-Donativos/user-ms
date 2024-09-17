from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from ..utils import validate_cpf


class Adress(BaseModel):
    country: str
    state: str
    city: str
    neighborhood: str
    street: str
    number: int


class User(BaseModel):
    name: str
    address: Adress
    email: EmailStr
    phone: str
    role: Literal["voluntario", "adminCD", "adminAbrigo", "superadmin"]
    codEntidade: int
    cpf: str = Field(..., description="CPF (Cadastro de Pessoas Físicas)")

    @field_validator("cpf")
    def cpf_validator(cls, v):
        return validate_cpf(v)
