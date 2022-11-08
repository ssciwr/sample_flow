import pytest
from circuit_seq_server import create_app


@pytest.fixture()
def app(tmp_path):
    temp_data_path = str(tmp_path)
    app = create_app(data_path=temp_data_path)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
