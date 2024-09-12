from unittest.mock import AsyncMock


class AsyncQuery(AsyncMock):
    async def to_list(self, *args, **kwargs):
        return []


class AsyncModel:
    save = AsyncMock()
