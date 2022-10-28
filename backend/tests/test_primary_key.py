from circuit_seq_server.primary_key import get_primary_key


def test_primary_key():
    assert get_primary_key(1, 0) == "1_A1"
    assert get_primary_key(1, 1) == "1_A2"
    assert get_primary_key(1, 95) == "1_H12"
    assert get_primary_key(1, 96) == None
