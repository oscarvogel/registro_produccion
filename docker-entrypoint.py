#!/usr/local/bin/python
"""Load a protected runtime env file before starting the application."""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path:
        return
    if not path.is_file():
        raise SystemExit(f"Required environment file not found: {path}")

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise SystemExit(f"Invalid environment line {line_number} in {path}")

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            raise SystemExit(f"Invalid environment key on line {line_number} in {path}")

        value = value.strip()
        comment_index = value.find(" #")
        if comment_index >= 0:
            value = value[:comment_index].rstrip()
        if value[:1] in {"'", '"'}:
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise SystemExit(f"Invalid quoted value on line {line_number} in {path}") from exc
        os.environ[key] = value


env_file = os.environ.get("REGISTRO_ENV_FILE")
if env_file:
    load_env_file(Path(env_file))

if len(sys.argv) < 2:
    raise SystemExit("No application command was provided")

os.execvp(sys.argv[1], sys.argv[1:])
