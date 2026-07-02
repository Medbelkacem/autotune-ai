#!/usr/bin/env python3
"""
Generate an ed25519 signing key pair for tuner-level recommendation approval.

Usage:
    python scripts/gen-signing-key.py [--out ./keys/tuner01]

Writes:
    <out>.priv.b64  — private key, keep offline / on hardware token only
    <out>.pub.b64   — public key, enroll in your user profile via /v1/auth/me
"""
from __future__ import annotations
import argparse
import pathlib
import sys

try:
    import nacl.signing
except ImportError:
    print("Install pynacl: pip install pynacl", file=sys.stderr)
    sys.exit(1)

import base64


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="./keys/tuner")
    args = p.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    sk = nacl.signing.SigningKey.generate()
    vk = sk.verify_key

    priv_b64 = base64.b64encode(bytes(sk)).decode()
    pub_b64 = base64.b64encode(bytes(vk)).decode()

    (out.with_suffix(".priv.b64")).write_text(priv_b64)
    (out.with_suffix(".pub.b64")).write_text(pub_b64)

    print(f"private -> {out.with_suffix('.priv.b64')}")
    print(f"public  -> {out.with_suffix('.pub.b64')}")
    print(f"pub_b64 = {pub_b64}")


if __name__ == "__main__":
    main()
