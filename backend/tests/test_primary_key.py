from circuit_seq_server.primary_key import get_primary_key


def test_primary_key_8_12():
    rows = 8
    cols = 12
    year = 2022
    assert get_primary_key(year, 1, 0, rows, cols) == "22_01_A1"
    assert get_primary_key(year, 1, 1, rows, cols) == "22_01_A2"
    assert get_primary_key(year, 1, 95, rows, cols) == "22_01_H12"
    assert get_primary_key(year, 1, 96, rows, cols) is None
