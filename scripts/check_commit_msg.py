#!/usr/bin/env python3
"""commit-msg-guardian
=====================
Validates that git commit messages follow Conventional Commits and are written
in English. Wired up as a pre-commit `commit-msg` hook (see .pre-commit-config.yaml).

Usage:
    python scripts/check_commit_msg.py <path-to-commit-msg-file>

Exit codes:
    0 = message accepted (commit allowed)
    1 = message rejected (commit blocked)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

ALLOWED_TYPES = {
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
}

# type(scope): subject   (scope optional)
PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9][a-z0-9/_-]*)\))?: (?P<subject>\S.*)$"
)

MAX_HEADER_LEN = 100

# Spanish-only characters: never valid in an English message
SPANISH_CHARS = re.compile(r"[áéíóúñü¿¡]")

# Spanish stopwords / vocabulary that must not appear in the subject line.
# (whole-word match only; words that are also valid English are excluded)
SPANISH_WORDS = {
    "al", "anadir", "anyadir", "archivo", "archivos", "carpeta", "carpetas",
    "como", "configuracion", "conexion", "con", "corregir", "crear",
    "cuando", "cuyo", "de", "del", "desde", "donde", "el", "ella", "ello",
    "eliminar", "en", "entre", "esas", "ese", "esos", "esta", "estas",
    "este", "estos", "estructura", "hasta", "hay", "implementar", "la",
    "las", "le", "les", "lo", "los", "mover", "muy", "ni", "o", "para",
    "pero", "por", "porque", "que", "reorganizar", "se", "ser", "sin",
    "sobre", "son", "su", "sus", "tambien", "tiene", "un", "una", "unas",
    "unos", "y", "ya",
}

# Messages that bypass validation entirely
SKIP_PREFIXES = ("Merge ", "fixup!", "squash!", "Revert \"")

EXAMPLE = 'example: feat(auth): add jwt token refresh'


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate(message: str) -> list[str]:
    """Return a list of human-readable errors (empty list = valid)."""
    # Drop comment lines git adds (# Please enter the commit message...)
    lines = [
        line for line in message.splitlines()
        if not line.lstrip().startswith("#")
    ]
    # Trim trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines or not lines[0].strip():
        return ["empty commit message"]

    header = lines[0].strip()
    errors: list[str] = []

    if header.startswith(SKIP_PREFIXES):
        return []

    match = PATTERN.match(header)
    if not match:
        errors.append(
            f'invalid format: "{header}"\n'
            f'    expected: type(scope): subject\n'
            f"    {EXAMPLE}"
        )
        # Cannot apply further header rules without a match
        return errors

    commit_type = match.group("type")
    if commit_type not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        errors.append(f'unknown type "{commit_type}" (allowed: {allowed})')

    subject = match.group("subject").strip()

    if len(header) > MAX_HEADER_LEN:
        errors.append(
            f"header is {len(header)} chars (max {MAX_HEADER_LEN})"
        )

    if subject[0].isupper():
        errors.append(
            'subject must start with a lowercase letter '
            f'(got "{subject[0]}")'
        )

    if subject.endswith("."):
        errors.append("subject must not end with a period")

    # --- English-only checks ------------------------------------------------
    if SPANISH_CHARS.search(message):
        found = sorted(set(SPANISH_CHARS.findall(message)))
        errors.append(
            f"Spanish characters are not allowed in English commits: "
            f"{' '.join(found)}"
        )

    subject_words = re.findall(r"[a-záéíóúñü]+", subject.lower())
    spanish_hits = [w for w in subject_words if w in SPANISH_WORDS]
    if spanish_hits:
        errors.append(
            "Spanish words in subject: "
            + ", ".join(f'"{w}"' for w in spanish_hits)
            + " — write the subject in English"
        )

    return errors


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        path = Path(argv[1])
        if not path.exists():
            print(f"commit-msg-guardian: file not found: {path}", file=sys.stderr)
            return 1
        message = path.read_text(encoding="utf-8", errors="replace")
    else:
        message = sys.stdin.read()

    errors = validate(message)

    if errors:
        print("commit-msg-guardian: commit message REJECTED", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        print(
            "\n  Format: type(scope): subject (lowercase, no period, <=100 chars)"
            f"\n  {EXAMPLE}",
            file=sys.stderr,
        )
        return 1

    print("commit-msg-guardian: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
