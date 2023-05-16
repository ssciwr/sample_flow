from __future__ import annotations
from typing import Dict
import io
import zipfile
from freezegun import freeze_time
import pathlib
import sample_flow_server
import flask_test_utils as ftu


@freeze_time("2022-11-21")
def test_remaining_mon(client):
    response = client.get("/api/remaining")
    assert response.json["remaining"] == 96


@freeze_time("2022-11-19")
def test_remaining_sat(client):
    response = client.get("/api/remaining")
    assert response.json["remaining"] == 0


def _get_auth_headers(
    client, email: str = "user@embl.de", password: str = "user"
) -> Dict:
    response = client.post("/api/login", json={"email": email, "password": password})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_invalid(client):
    # missing json
    response = client.post("/api/login")
    assert response.status_code > 200
    # unknown email
    response = client.post("/api/login", json={"email": "", "password": ""})
    assert response.status_code == 401
    assert response.json["message"] == "Unknown email address"
    # wrong password
    response = client.post("/api/login", json={"email": "user@embl.de", "password": ""})
    assert response.status_code == 401
    assert response.json["message"] == "Incorrect password"


def test_login_valid(client):
    email = "user@embl.de"
    password = "user"
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["user"]["email"] == email
    assert response.json["user"]["is_admin"] is False


def test_change_password_invalid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/login", json={"email": "user@embl.de", "password": "user"}
    )
    assert response.status_code == 200
    response = client.post(
        "/api/change_password",
        headers=headers,
        json={"current_password": "wrong", "new_password": "abc123"},
    )
    assert response.status_code == 401
    assert "Failed to change password" in response.json["message"]
    response = client.post(
        "/api/change_password", headers=headers, json={"new_password": "abc123"}
    )
    assert response.status_code == 401
    assert response.json["message"] == "Current password missing"
    response = client.post(
        "/api/change_password", headers=headers, json={"current_password": "abc123"}
    )
    assert response.status_code == 401
    assert response.json["message"] == "New password missing"


def test_change_password_valid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/login", json={"email": "user@embl.de", "password": "user"}
    )
    assert response.status_code == 200
    response = client.post(
        "/api/change_password",
        headers=headers,
        json={"current_password": "user", "new_password": "abc123"},
    )
    assert response.status_code == 200
    assert "Password changed" in response.json["message"]
    response = client.post(
        "/api/login", json={"email": "user@embl.de", "password": "user"}
    )
    assert response.status_code == 401
    response = client.post(
        "/api/login", json={"email": "user@embl.de", "password": "abc123"}
    )
    assert response.status_code == 200


def test_jwt_same_secret_persists_valid_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "0123456789abcdefghijklmnopqrstuvwxyz")
    app1 = sample_flow_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/api/samples", headers=headers1).status_code == 200
    # create new app with same JWT secret key & user database
    app2 = sample_flow_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can re-use the same JWT token in the new app
    assert client2.get("/api/samples", headers=headers1).status_code == 200


def test_jwt_different_secret_invalidates_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app1 = sample_flow_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/api/samples", headers=headers1).status_code == 200
    # create new app with a different JWT secret key & user database
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app2 = sample_flow_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can't re-use the same JWT token in the new app
    assert client2.get("/api/samples", headers=headers1).status_code == 422


def test_samples_invalid(client):
    # no auth header
    response = client.get("/api/samples")
    assert response.status_code == 401


def test_samples_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/api/samples", headers=headers)
    assert response.status_code == 200
    assert "current_samples" in response.json
    assert "previous_samples" in response.json


def test_running_options_invalid(client):
    # no auth header
    response = client.get("/api/running_options")
    assert response.status_code == 401


def test_running_options_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/api/running_options", headers=headers)
    assert response.status_code == 200
    assert "running_options" in response.json


@freeze_time("2022-11-21")
def test_sample_mon_fasta(client, ref_seq_fasta):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "r Q",
            "concentration": 97,
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
    assert new_sample["concentration"] == 97
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_fasta_invalid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "r",
            "concentration": 34,
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
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "r23",
            "concentration": 11,
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
    assert new_sample["concentration"] == 11
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_genbank(client, ref_seq_genbank):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "run1",
            "concentration": 177,
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
    assert new_sample["concentration"] == 177
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_snapgene(client, ref_seq_snapgene):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "run1",
            "concentration": 131,
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
    assert new_sample["concentration"] == 131
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


@freeze_time("2022-11-21")
def test_sample_mon_snapgene_noid(client, ref_seq_snapgene_noid):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "run1",
            "concentration": 111,
            "file": (ref_seq_snapgene_noid, "test_file.dna"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    new_sample = response.json["sample"]
    assert new_sample["email"] == "user@embl.de"
    assert new_sample["name"] == "abc"
    assert new_sample["primary_key"] == "22_47_A1"
    # fallback to filename for description if no id present in file:
    assert new_sample["reference_sequence_description"] == "test_file"
    assert new_sample["running_option"] == "run1"
    assert new_sample["concentration"] == 111
    data_path = pathlib.Path(client.application.config.get("CIRCUITSEQ_DATA_PATH"))
    fasta_path = data_path / "2022/47/inputs/references/22_47_A1_abc.fasta"
    assert fasta_path.is_file()
    with fasta_path.open() as f:
        assert new_sample["reference_sequence_description"] in f.readline()


def test_result_invalid(client):
    response = client.post(
        "/api/result", json={"primary_key": "XYZ", "filetype": "zip"}
    )
    assert response.status_code == 401
    headers = _get_auth_headers(client, "user@embl.de", "user")
    response = client.post(
        "/api/result", json={"primary_key": "XYZ", "filetype": "zip"}, headers=headers
    )
    assert response.status_code == 401
    assert f"Sample not found" in response.json["message"]
    key = "22_46_A2"
    for filetype in ["exe", "txt"]:
        response = client.post(
            "/api/result",
            json={"primary_key": key, "filetype": filetype},
            headers=headers,
        )
        assert response.status_code == 401
        assert f"Invalid filetype {filetype}" in response.json["message"]
    for filetype in ["fasta", "gbk", "zip"]:
        response = client.post(
            "/api/result",
            json={"primary_key": key, "filetype": filetype},
            headers=headers,
        )
        assert response.status_code == 401
        assert f"No {filetype} results available" in response.json["message"]


def _upload_result(client, result_zipfile: pathlib.Path, primary_key: str = None):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    if primary_key is None:
        primary_key = result_zipfile.stem[0:8]
    with open(result_zipfile, "rb") as f:
        response = client.post(
            "/api/admin/result",
            data={
                "primary_key": primary_key,
                "success": True,
                "file": (io.BytesIO(f.read()), result_zipfile.name),
            },
            headers=headers,
        )
    return response


def test_result_valid(client, result_zipfiles):
    headers = _get_auth_headers(client, "user@embl.de", "user")
    key = "22_46_A2"
    assert _upload_result(client, result_zipfiles[0]).status_code == 200
    for filetype in ["fasta", "gbk", "zip"]:
        response = client.post(
            "/api/result",
            json={"primary_key": key, "filetype": filetype},
            headers=headers,
        )
        assert response.status_code == 200
        assert len(response.data) > 1


def test_admin_settings_invalid(client):
    # no auth header
    response = client.get("/api/admin/settings")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/settings", headers=headers)
    assert response.status_code == 401


def test_admin_settings_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/api/admin/settings", headers=headers)
    assert response.status_code == 200
    assert response.json["plate_n_rows"] == 8
    assert response.json["plate_n_cols"] == 12
    # set new valid settings
    response = client.post(
        "/api/admin/settings",
        json={
            "plate_n_rows": 14,
            "plate_n_cols": 18,
            "running_options": ["o1", "o2", "o3"],
            "last_submission_day": 4,
        },
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get("/api/admin/settings", headers=headers)
    assert response.status_code == 200
    assert response.json["plate_n_rows"] == 14
    assert response.json["plate_n_cols"] == 18
    assert response.json["running_options"] == ["o1", "o2", "o3"]
    assert response.json["last_submission_day"] == 4


def test_admin_samples_invalid(client):
    # no auth header
    response = client.get("/api/admin/samples")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/samples", headers=headers)
    assert response.status_code == 401


def test_admin_samples_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/api/admin/samples", headers=headers)
    assert response.status_code == 200
    assert "current_samples" in response.json
    assert "previous_samples" in response.json


def test_admin_token_invalid(client):
    # no auth header
    response = client.get("/api/admin/token")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/token", headers=headers)
    assert response.status_code == 401


def test_admin_token_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/api/admin/token", headers=headers)
    assert response.status_code == 200
    new_token = response.json["access_token"]
    assert (
        client.get(
            "/api/admin/samples", headers={"Authorization": f"Bearer {new_token}"}
        ).status_code
        == 200
    )


def test_admin_users_invalid(client):
    # no auth header
    response = client.get("/api/admin/users")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 401


def test_admin_users_valid(client):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 200
    assert "users" in response.json


def test_admin_zipsamples_invalid(client):
    # no auth header
    response = client.post("/api/admin/zipsamples")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.post("/api/admin/zipsamples", headers=headers)
    assert response.status_code == 401


@freeze_time("2022-11-21")
def test_admin_zipsamples_valid(client, ref_seq_fasta):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    # upload a sample
    response = client.post(
        "/api/sample",
        data={
            "name": "abc",
            "running_option": "r Q",
            "concentration": 97,
            "file": (ref_seq_fasta, "test.fa"),
        },
        headers=headers,
    )
    assert response.status_code == 200
    # get samples tsv
    response = client.post("/api/admin/zipsamples", headers=headers)
    assert response.status_code == 200
    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    filenames = [f.filename for f in zip_file.filelist]
    assert len(filenames) == 3
    assert "samples.tsv" in filenames
    assert "references/" in filenames
    assert "references/22_47_A1_abc.fasta" in filenames
    tsv_lines = zip_file.read("samples.tsv").splitlines()
    assert len(tsv_lines) == 2
    assert (
        tsv_lines[0]
        == b"date\tprimary_key\ttube_primary_key\temail\tname\trunning_option\tconcentration"
    )
    assert (
        tsv_lines[1] == b"2022-11-21\t22_47_A1\t22_47_A1\tadmin@embl.de\tabc\tr Q\t97"
    )


def test_admin_result_valid(client, result_zipfiles):
    for result_zipfile in result_zipfiles:
        response = _upload_result(client, result_zipfile)
        assert response.status_code == 200
        assert result_zipfile.name in response.json["message"]


@freeze_time("2022-11-21")
def test_admin_resubmit_sample_valid(client, result_zipfiles):
    headers = _get_auth_headers(client, "admin@embl.de", "admin")
    primary_key = "22_46_A2"
    new_primary_key = "22_47_A1"
    response = client.post(
        "/api/admin/resubmit_sample",
        json={"primary_key": primary_key},
        headers=headers,
    )
    assert response.status_code == 200
    assert primary_key in response.json["message"]
    assert new_primary_key in response.json["message"]
    response = client.get("/api/admin/samples", headers=headers)
    assert len(response.json["current_samples"]) == 1
    resubmitted_sample = response.json["current_samples"][0]
    print(response.json["previous_samples"])
    original_sample = [
        d for d in response.json["previous_samples"] if d["primary_key"] == primary_key
    ][0]
    assert resubmitted_sample["id"] > original_sample["id"]
    assert resubmitted_sample["primary_key"] == "22_47_A1"
    assert resubmitted_sample["email"] == "RESUBMITTED"
    keys_that_should_differ = ["id", "primary_key", "date", "email"]
    for key, value in original_sample.items():
        if key not in keys_that_should_differ:
            assert value == resubmitted_sample[key]
    # uploading a result for new primary key -> original primary key
    response = _upload_result(client, result_zipfiles[0], "22_47_A1")
    assert response.status_code == 200
    assert primary_key in response.json["message"]
