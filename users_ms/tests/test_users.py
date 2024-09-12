from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from .mocks.users import AsyncModel, AsyncQuery


def test_get_users(
    client: TestClient,
    headers: dict[str, str],
):
    """
    Pytest will inject parameters with names
    matching any fixture we have declared.

    Which means that, internaly, pytest will
    call the fixture "client" - or retrieve its
    cached value - and pass it as an argument
    to this function. The same will happen
    for the "headers" parameter.
    """

    # Note that the path is relative to where the function
    # is **used**, not where it is defined
    target_fn = "app.api.users.controller.models.User.all"
    with patch(target_fn) as mock_all:
        mock_all.return_value = AsyncQuery()
        response = client.get("/api/users", headers=headers)
        mock_all.assert_called_once()

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_user(
    async_client: AsyncClient,
    headers: dict[str, str],
):
    """
    With the help of the module "pytest-mock" we are able
    to write async tests. We just need to mark the test
    function as "async" and use the "await" keyword
    before any async call.

    Everything works the same, parameter inject, assertions,
    etc.
    """

    body = {
        "first_name": "Test",
        "last_name": "User",
        "email": "user@test.com",
    }

    # Note that we are mocking the class, not a function
    # from the class. We do that so we can inspect that
    # "save" method has been awaited exactly once.
    target_fn = "app.api.users.controller.models.User"
    with patch(target_fn) as mock_all:
        mock_all.return_value = AsyncModel()
        response = await async_client.post(
            "/api/users", json=body, headers=headers, follow_redirects=True
        )
        mock_all.return_value.save.assert_awaited_once()

    assert response.status_code == 201
