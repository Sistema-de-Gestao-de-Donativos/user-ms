
from pydantic import BaseModel, Field
from typing import Annotated

from schemas.Users import UsersBaseInfo, UsersTyping
from schemas.Validators import Typing


class AuthTyping(Typing):
    """Define the typing for the Auth schema. It is used for the type hinting and the validation of the schema."""

    access_token = Annotated[str, Field(..., examples=["any.valid.jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"],
                                        description="A JWT used to authenticate the user. Returned from the login endpoint.")]

    refresh_token = Annotated[str, Field(..., examples=["any.valid.jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"],
                                         description="A JWT used to refresh the access token. Returned from the login endpoint.")]

    reset_token = Annotated[str, Field(..., examples=["any.valid.jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"],
                                       description="A JWT received from the invite endpoint. Used to reset the user's default password and enable the user to login.")]

    token_type = Annotated[str, Field(..., examples=["bearer"],
                                      description="The type of the token. Always 'bearer'.")]

    login_info = Annotated[UsersBaseInfo, Field(examples=[UsersBaseInfo(name=UsersTyping().get_field(
        "name", "examples")).model_dump_json()], description="The user's basic information for the UI. Returned from the login endpoint.")]


class TokenResponse(BaseModel):
    access_token: AuthTyping.access_token
    token_type: AuthTyping.token_type


class LoginResponse(TokenResponse):
    info: AuthTyping.login_info
    refresh_token: AuthTyping.refresh_token
