import pytest
import uuid
import httpx
from app.main import app
from app.core.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "JobGuard AI" in data["service"]

@pytest.mark.asyncio
async def test_user_registration_and_login():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"
    name = "Alex Developer"

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register
        reg_response = await client.post(
            "/api/auth/register",
            json={"name": name, "email": email, "password": password}
        )
        assert reg_response.status_code == 201
        user_data = reg_response.json()
        assert user_data["email"] == email
        assert user_data["name"] == name
        assert "id" in user_data

        # 2. Duplicate registration should fail with 400
        dup_response = await client.post(
            "/api/auth/register",
            json={"name": name, "email": email, "password": password}
        )
        assert dup_response.status_code == 400

        # 3. Login with correct credentials
        login_response = await client.post(
            "/api/auth/login",
            json={"email": email, "password": password}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # 4. Login with wrong password should fail with 401
        bad_login = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "WrongPassword"}
        )
        assert bad_login.status_code == 401

        # 5. Access /api/auth/me with Bearer token
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == email
        assert me_data["name"] == name

        # 6. Access /api/profile
        profile_response = await client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["full_name"] == name

        # 7. Update profile
        update_response = await client.put(
            "/api/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "preferred_titles": "Senior Python Developer, Backend Architect",
                "preferred_locations": "San Francisco, CA; Remote",
                "remote_preference": "Remote",
                "expected_salary": 140000,
                "key_skills": "Python, FastAPI, PostgreSQL, Docker"
            }
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["remote_preference"] == "Remote"
        assert updated_data["expected_salary"] == 140000
        assert "Docker" in updated_data["key_skills"]
