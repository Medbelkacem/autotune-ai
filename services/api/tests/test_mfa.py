from app.core.mfa import new_secret, provisioning_uri, totp_now, totp_verify


def test_totp_roundtrip():
    s = new_secret()
    code = totp_now(s)
    assert totp_verify(s, code)


def test_totp_rejects_wrong():
    s = new_secret()
    assert not totp_verify(s, "000000")
    assert not totp_verify(s, "abcdef")
    assert not totp_verify(s, "")


def test_provisioning_uri_shape():
    s = new_secret()
    uri = provisioning_uri(email="a@b.com", issuer="AutoTune AI", secret=s)
    assert uri.startswith("otpauth://totp/")
    assert "issuer=AutoTune%20AI" in uri
    assert "algorithm=SHA1" in uri
