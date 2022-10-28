import circuit_seq_server


def test_circuit_seq_server():
    assert circuit_seq_server.add_one(1) == 2
