from fastapi import status
from pydantic import BaseModel
from typing import Generic, TypeVar


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    message: str
    data: T = None
    status_code: int = status.HTTP_200_OK
    success: bool = True
    time_elapsed: float | None = None

    class Config:
        arbitrary_types_allowed = True


class ApiResponseList(ApiResponse[T]):

    class ApiResponseListData(BaseModel, Generic[T]):
        total_count: int
        filtered_list: list[T]

    data: ApiResponseListData[T] = None


def TestApiResponse(
    response,
    status_code: status = status.HTTP_200_OK,
    message: str = None,
    data=None,
    retrieveData: bool = False,
    success: bool = True,
    time_elapsed: float = None,
):
    response = response.json()
    assert response["success"] == success
    if message:
        assert response["message"] == message
    if data:
        assert response["data"] == data
    assert response["status_code"] == status_code
    if time_elapsed:
        assert response["time_elapsed"] <= time_elapsed
    return response["data"] if retrieveData else True


def TestApiResponseException(
    response,
    status_code: status = status.HTTP_400_BAD_REQUEST,
    detail: str = None,
):
    assert response.status_code == status_code
    response = response.json()
    if detail:
        assert response["detail"] == detail
    return True
