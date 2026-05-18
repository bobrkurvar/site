from infra.security import get_hash, verify


def test_generate_hash_and_verify():
    password = "password"
    hash = get_hash(password)
    assert verify(password, hash)