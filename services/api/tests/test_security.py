import json

from app.core.security import (
    fingerprint,
    generate_signing_key,
    hash_password,
    sign_blob,
    verify_password,
    verify_signature,
)


def test_password_hash_roundtrip():
    h = hash_password("correcthorsebatterystaple")
    assert verify_password("correcthorsebatterystaple", h)
    assert not verify_password("wrong", h)


def test_ed25519_signature_roundtrip():
    sk, vk = generate_signing_key()
    payload = json.dumps({"foo": 1, "bar": [2, 3]}, sort_keys=True).encode()
    sig = sign_blob(payload, sk)
    assert verify_signature(payload, sig, vk)
    assert not verify_signature(payload + b"tampered", sig, vk)
    assert len(fingerprint(vk)) == 16
