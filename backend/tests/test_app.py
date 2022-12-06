from __future__ import annotations
from typing import Dict
import io
import zipfile
from freezegun import freeze_time
import pathlib
import circuit_seq_server
import flask_test_utils as ftu


@freeze_time("2022-11-21")
def test_remaining_mon(client):
    response = client.get("/remaining")
    assert response.json["remaining"] == 96


@freeze_time("2022-11-19")
def test_remaining_sat(client):
    response = client.get("/remaining")
    assert response.json["remaining"] == 0


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


def test_change_password_invalid(client):
    headers = _get_auth_headers(client)
    response = client.post("/login", json={"email": "user@embl.de", "password": "user"})
    assert response.status_code == 200
    response = client.post(
        "/change_password",
        headers=headers,
        json={"current_password": "wrong", "new_password": "abc123"},
    )
    assert response.status_code == 401
    assert "Failed to change password" in response.json
    response = client.post(
        "/change_password", headers=headers, json={"new_password": "abc123"}
    )
    assert response.status_code == 401
    assert response.json == "Current password missing"
    response = client.post(
        "/change_password", headers=headers, json={"current_password": "abc123"}
    )
    assert response.status_code == 401
    assert response.json == "New password missing"


def test_change_password_valid(client):
    headers = _get_auth_headers(client)
    response = client.post("/login", json={"email": "user@embl.de", "password": "user"})
    assert response.status_code == 200
    response = client.post(
        "/change_password",
        headers=headers,
        json={"current_password": "user", "new_password": "abc123"},
    )
    assert response.status_code == 200
    assert "Password changed" in response.json
    response = client.post("/login", json={"email": "user@embl.de", "password": "user"})
    assert response.status_code == 401
    response = client.post(
        "/login", json={"email": "user@embl.de", "password": "abc123"}
    )
    assert response.status_code == 200


def test_jwt_same_secret_persists_valid_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "0123456789abcdefghijklmnopqrstuvwxyz")
    app1 = circuit_seq_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/samples", headers=headers1).status_code == 200
    # create new app with same JWT secret key & user database
    app2 = circuit_seq_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can re-use the same JWT token in the new app
    assert client2.get("/samples", headers=headers1).status_code == 200


def test_jwt_different_secret_invalidates_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app1 = circuit_seq_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/samples", headers=headers1).status_code == 200
    # create new app with a different JWT secret key & user database
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app2 = circuit_seq_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can't re-use the same JWT token in the new app
    assert client2.get("/samples", headers=headers1).status_code == 422


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


def test_running_options_invalid(client):
    # no auth header
    response = client.get("/running_options")
    assert response.status_code == 401


def test_running_options_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/running_options", headers=headers)
    assert response.status_code == 200
    assert "running_options" in response.json


@freeze_time("2022-11-21")
def test_sample_mon_fasta(client, ref_seq_fasta):
    headers = _get_auth_headers(client)
    response = client.post(
        "/sample",
        data={
            "name": "abc",
            "running_option": "r Q",
            "file": (ref_seq_fasta, "test.fa"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    new_sample = response.json["sample"]
    assert new_sample["email"] == "user@embl.de"
    assert new_sample["name"] == "abc"
    assert new_sample["primary_key"] == "22_47_A1"
    assert new_sample["reference_sequence_description"] == "seq0"
    assert new_sample["running_option"] == "r Q"
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_fasta_invalid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/sample",
        data={
            "name": "abc",
            "running_option": "r",
            "file": (io.BytesIO(b"invalid_fasta_contents"), "test.fa"),
        },
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json["message"] == "Failed to parse reference sequence file."
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/46/inputs/references/22_46_A1_abc.fasta"
    assert not fasta_path.is_file()


@freeze_time("2022-11-21")
def test_sample_mon_embl(client, ref_seq_embl):
    headers = _get_auth_headers(client)
    response = client.post(
        "/sample",
        data={
            "name": "abc",
            "running_option": "r23",
            "file": (ref_seq_embl, "test.embl"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    new_sample = response.json["sample"]
    assert new_sample["email"] == "user@embl.de"
    assert new_sample["name"] == "abc"
    assert new_sample["primary_key"] == "22_47_A1"
    assert new_sample["reference_sequence_description"] == "X56734.1"
    assert new_sample["running_option"] == "r23"
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_genbank(client, ref_seq_genbank):
    headers = _get_auth_headers(client)
    response = client.post(
        "/sample",
        data={
            "name": "abc",
            "running_option": "run1",
            "file": (ref_seq_genbank, "test.gbk"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    new_sample = response.json["sample"]
    assert new_sample["email"] == "user@embl.de"
    assert new_sample["name"] == "abc"
    assert new_sample["primary_key"] == "22_47_A1"
    assert new_sample["reference_sequence_description"] == "Z78533.1"
    assert new_sample["running_option"] == "run1"
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_snapgene(client, ref_seq_snapgene):
    headers = _get_auth_headers(client)
    response = client.post(
        "/sample",
        data={
            "name": "abc",
            "running_option": "run1",
            "file": (ref_seq_snapgene, "test.dna"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    new_sample = response.json["sample"]
    assert new_sample["email"] == "user@embl.de"
    assert new_sample["name"] == "abc"
    assert new_sample["primary_key"] == "22_47_A1"
    assert new_sample["reference_sequence_description"] == "BlueScribe"
    assert new_sample["running_option"] == "run1"
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


def test_result_invalid(client, result_zipfiles):
    response = client.post("/result", json={"primary_key": "XYZ", "filetype": "zip"})
    assert response.status_code == 401
    headers = _get_auth_headers(client, "user@embl.de", "user")
    response = client.post(
        "/result", json={"primary_key": "XYZ", "filetype": "zip"}, headers=headers
    )
    assert response.status_code == 401
    assert f"Sample not found" in response.json
    key = "22_46_A2"
    for filetype in ["exe", "txt"]:
        response = client.post(
            "/result", json={"primary_key": key, "filetype": filetype}, headers=headers
        )
        assert response.status_code == 401
        assert f"Invalid filetype {filetype}" in response.json
    for filetype in ["fasta", "gbk", "zip"]:
        response = client.post(
            "/result", json={"primary_key": key, "filetype": filetype}, headers=headers
        )
        assert response.status_code == 401
        assert f"No {filetype} results available" in response.json


def _upload_result(client, result_zipfile):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    with open(result_zipfile, "rb") as f:
        response = client.post(
            "/admin/result",
            data={
                "file": (io.BytesIO(f.read()), result_zipfile.name),
            },
            headers=headers,
        )
    return response


def test_result_valid(client, result_zipfiles):
    headers = _get_auth_headers(client, "user@embl.de", "user")
    key = "22_46_A2"
    _upload_result(client, result_zipfiles[0])
    for filetype in ["fasta", "gbk", "zip"]:
        response = client.post(
            "/result", json={"primary_key": key, "filetype": filetype}, headers=headers
        )
        assert response.status_code == 200
        assert len(response.data) > 1


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
        json={
            "plate_n_rows": 14,
            "plate_n_cols": 18,
            "running_options": ["o1", "o2", "o3"],
            "last_submission_day": 4,
        },
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get("/admin/settings", headers=headers)
    assert response.status_code == 200
    assert response.json["plate_n_rows"] == 14
    assert response.json["plate_n_cols"] == 18
    assert response.json["running_options"] == ["o1", "o2", "o3"]
    assert response.json["last_submission_day"] == 4


def test_admin_samples_invalid(client):
    # no auth header
    response = client.get("/admin/samples")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/samples", headers=headers)
    assert response.status_code == 401


def test_admin_samples_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/samples", headers=headers)
    assert response.status_code == 200
    assert "current_samples" in response.json
    assert "previous_samples" in response.json


def test_admin_token_invalid(client):
    # no auth header
    response = client.get("/admin/token")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/token", headers=headers)
    assert response.status_code == 401


def test_admin_token_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/token", headers=headers)
    assert response.status_code == 200
    new_token = response.json["access_token"]
    assert (
        client.get(
            "/admin/samples", headers={"Authorization": f"Bearer {new_token}"}
        ).status_code
        == 200
    )


def test_admin_users_invalid(client):
    # no auth header
    response = client.get("/admin/users")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 401


def test_admin_users_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200
    assert "users" in response.json


def test_admin_zipsamples_invalid(client):
    # no auth header
    response = client.post("/admin/zipsamples")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.post("/admin/zipsamples", headers=headers)
    assert response.status_code == 401


def test_admin_zipsamples_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.post("/admin/zipsamples", headers=headers)
    assert response.status_code == 200
    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    assert len(zip_file.filelist) == 1
    assert zip_file.filelist[0].filename == "samples.tsv"
    tsv = zip_file.read("samples.tsv")
    assert tsv == b"date\tprimary_key\temail\tname\trunning_option\n"


def test_admin_result_valid(client, result_zipfiles):
    for result_zipfile in result_zipfiles:
        response = _upload_result(client, result_zipfile)
        assert response.status_code == 200
        assert result_zipfile.name in response.json["message"]
