from typing import Dict


def test_remaining(client):
    response = client.get("/remaining")
    assert response.json["remaining"] == 96


def _get_auth_headers(
    client, email: str = "user@embl.de", password: str = "user"
) -> Dict:
    response = client.post("/login", json={"email": email, "password": password})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_invalid(client):
    # missing json
    response = client.post("/login")
    assert response.status_code == 400
    # unknown email
    response = client.post("/login", json={"email": "", "password": ""})
    assert response.status_code == 401
    assert response.json == "Unknown email address"
    # wrong password
    response = client.post("/login", json={"email": "user@embl.de", "password": ""})
    assert response.status_code == 401
    assert response.json == "Incorrect password"


def test_login_valid(client):
    email = "user@embl.de"
    password = "user"
    response = client.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["user"]["email"] == email
    assert response.json["user"]["is_admin"] is False


def test_samples_invalid(client):
    # no auth header
    response = client.get("/samples")
    assert response.status_code == 401


def test_samples_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/samples", headers=headers)
    assert response.status_code == 200
    assert "current_samples" in response.json
    assert "previous_samples" in response.json


def test_admin_settings_invalid(client):
    # no auth header
    response = client.get("/admin/settings")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/settings", headers=headers)
    assert response.status_code == 401


def test_admin_settings_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/settings", headers=headers)
    assert response.status_code == 200
    assert response.json["plate_n_rows"] == 8
    assert response.json["plate_n_cols"] == 12
    # set new valid settings
    response = client.post(
        "/admin/settings",
        json={"plate_n_rows": 14, "plate_n_cols": 18},
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get("/admin/settings", headers=headers)
    assert response.status_code == 200
    assert response.json["plate_n_rows"] == 14
    assert response.json["plate_n_cols"] == 18


def test_admin_allsamples_invalid(client):
    # no auth header
    response = client.get("/admin/allsamples")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/allsamples", headers=headers)
    assert response.status_code == 401


def test_admin_allsamples_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/allsamples", headers=headers)
    assert response.status_code == 200
    assert "current_samples" in response.json
    assert "previous_samples" in response.json


def test_admin_allusers_invalid(client):
    # no auth header
    response = client.get("/admin/allusers")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/allusers", headers=headers)
    assert response.status_code == 401


def test_admin_allusers_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/allusers", headers=headers)
    assert response.status_code == 200
    assert "users" in response.json