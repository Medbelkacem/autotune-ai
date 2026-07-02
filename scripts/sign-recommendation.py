#!/usr/bin/env python3
"""
Sign a recommendation bundle with an ed25519 private key.

Usage:
    python scripts/sign-recommendation.py \
        --priv keys/tuner.priv.b64 \
        --bundle bundle.json \
        > signature.txt
"""
from __future__ import annotations
import argparse
import base64
import json
import pathlib
import sys

try:
    import nacl.signing
except ImportError:
    print("Install pynacl: pip install pynacl", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--priv", required=True)
    p.add_argument("--bundle", required=True)
    a = p.parse_args()

    priv_b64 = pathlib.Path(a.priv).read_text().strip()
    bundle = json.loads(pathlib.Path(a.bundle).read_text())
    canonical = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()

    sk = nacl.signing.SigningKey(base64.b64decode(priv_b64))
    sig = sk.sign(canonical).signature
    print(base64.b64encode(sig).decode())


if __name__ == "__main__":
    main()
