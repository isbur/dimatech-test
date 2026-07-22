import pytest
from sanic import Sanic


@pytest.mark.asyncio
async def test_health(app: Sanic) -> None:
    _request, response = await app.asgi_client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
