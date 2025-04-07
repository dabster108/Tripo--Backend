# import os
# import pytest
# from httpx import AsyncClient
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Import the FastAPI app from your main module
# from app.main import app

# # Fixture to initialize the FastAPI app
# @pytest.fixture(scope="function")
# async def client():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac

# # Test the root endpoint
# @pytest.mark.asyncio
# async def test_root(client: AsyncClient):
#     response = await client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Welcome to Tripo API"}

# # Test CORS middleware
# @pytest.mark.asyncio
# async def test_cors_middleware(client: AsyncClient):
#     # Test allowed origin
#     origin = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")[0]
#     headers = {"Origin": origin}
#     response = await client.get("/", headers=headers)
#     assert response.status_code == 200
#     assert "access-control-allow-origin" in response.headers
#     assert response.headers["access-control-allow-origin"] == origin

#     # Test disallowed origin
#     headers = {"Origin": "http://disallowed-origin.com"}
#     response = await client.get("/", headers=headers)
#     assert response.status_code == 200
#     assert "access-control-allow-origin" not in response.headers

# # Test health endpoint
# @pytest.mark.asyncio
# async def test_health_endpoint(client: AsyncClient):
#     response = await client.get("/api/v1/health")
#     assert response.status_code == 200
#     assert "status" in response.json()

# # Test auth endpoint (example)
# @pytest.mark.asyncio
# async def test_auth_endpoint(client: AsyncClient):
#     response = await client.post("/api/v1/auth/login", json={"username": "test", "password": "test"})
#     assert response.status_code == 200
#     assert "access_token" in response.json()