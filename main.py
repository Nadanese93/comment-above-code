#!/usr/bin/env python3
"""Write the contest entry: one comment line to entry.txt.

Stdlib only. Output goes to MAKEFUN_OUTPUT_DIR (default ./output).
The entry is a single line with no trailing newline.
"""

import hashlib
import os

ENTRY = "// Checkout works because the warehouse clock is 11 minutes slow. Fix NTP and orders ship yesterday."
EXPECTED_SHA256 = "a2b585b19dbc753413bd95c01d5495808295c4bc54763e8503e6220ebb024ce9"


def _remove_corrupt(path):
    try:
        os.remove(path)
    except OSError:
        pass


def verify(path):
    """Read entry.txt back from disk and validate it.

    Checks valid UTF-8, length 1-200 chars, a single line with no
    trailing or middle newline, no control characters, and that the
    canonical sha256 matches the expected entry. A corrupt file is
    removed. Returns True only when the file on disk is exactly the
    expected entry.
    """
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        print("verify failed: cannot read %s: %s" % (path, exc))
        return False
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        print("verify failed: %s is not valid UTF-8" % path)
        _remove_corrupt(path)
        return False
    if not 1 <= len(text) <= 200:
        print("verify failed: entry length %d out of range 1-200" % len(text))
        _remove_corrupt(path)
        return False
    if "\n" in text or "\r" in text:
        print("verify failed: entry must be a single line")
        _remove_corrupt(path)
        return False
    if text != text.strip():
        print("verify failed: entry must not have leading/trailing whitespace")
        _remove_corrupt(path)
        return False
    for ch in text:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            print("verify failed: control character U+%04X" % ord(ch))
            _remove_corrupt(path)
            return False
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        print("verify failed: sha256 %s != expected %s" % (digest, EXPECTED_SHA256))
        _remove_corrupt(path)
        return False
    return True


def main():
    if not 1 <= len(ENTRY) <= 200:
        raise SystemExit("entry length %d out of range 1-200" % len(ENTRY))
    if ENTRY != ENTRY.strip() or "\n" in ENTRY:
        raise SystemExit("entry must be a single non-blank line")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in ENTRY):
        raise SystemExit("entry must not contain control characters")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    if not verify(path):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
