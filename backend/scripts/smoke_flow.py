import os
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
import app.models as models  # noqa: F401


def main():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    run_id = uuid4().hex[:8]
    email = os.getenv("SMOKE_EMAIL", f"flow-{run_id}@example.com")
    password = os.getenv("SMOKE_PASSWORD", "secret123")
    other_email = os.getenv("SMOKE_OTHER_EMAIL", f"other-{run_id}@example.com")

    assert client.get("/health").status_code == 200

    register = client.post("/api/auth/register", json={"name": "流程家长", "email": email, "password": password})
    if register.status_code not in (200, 400):
        raise RuntimeError(register.text)

    login = client.post("/api/auth/login", json={"email": email, "password": password})
    login.raise_for_status()
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.get("/api/auth/me", headers=headers).raise_for_status()

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0P\x0f\x00\x05\x83"
        b"\x02\x7f\x94\xda\x95\xd9\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    upload = client.post("/api/upload", headers=headers, files={"file": ("wrong.png", png, "image/png")})
    upload.raise_for_status()
    upload_data = upload.json()

    analyze = client.post("/api/analyze", headers=headers, json=upload_data)
    analyze.raise_for_status()

    create = client.post("/api/mistakes", headers=headers, json={**upload_data, **analyze.json()})
    create.raise_for_status()
    mistake_id = create.json()["id"]

    assert len(client.get("/api/mistakes", headers=headers).json()) >= 1
    assert len(client.get("/api/review/today", headers=headers).json()) >= 1
    client.post(f"/api/review/{mistake_id}/submit", headers=headers, json={"result": "correct"}).raise_for_status()
    dashboard = client.get("/api/dashboard", headers=headers)
    dashboard.raise_for_status()
    assert dashboard.json()["total"] >= 1

    relogin = client.post("/api/auth/login", json={"email": email, "password": password})
    relogin.raise_for_status()
    relogin_headers = {"Authorization": f"Bearer {relogin.json()['access_token']}"}
    client.get(f"/api/mistakes/{mistake_id}", headers=relogin_headers).raise_for_status()

    other_register = client.post("/api/auth/register", json={"name": "隔离测试家长", "email": other_email, "password": password})
    other_register.raise_for_status()
    other_login = client.post("/api/auth/login", json={"email": other_email, "password": password})
    other_login.raise_for_status()
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
    assert client.get(f"/api/mistakes/{mistake_id}", headers=other_headers).status_code == 404
    assert client.get(upload_data["image_url"], headers=other_headers).status_code == 404

    blocked = client.get("/api/mistakes")
    assert blocked.status_code in (401, 403)
    print("FLOW_OK")


if __name__ == "__main__":
    main()
