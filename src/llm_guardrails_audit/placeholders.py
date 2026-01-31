from __future__ import annotations
import re
import yaml
from typing import Dict

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

def load_placeholders(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def apply_placeholders(prompt: str, values: Dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1)
        return values.get(key, f"{{{{{key}}}}}")  # keep token if missing
    return TOKEN_RE.sub(repl, prompt)

def find_missing(prompt: str, values: Dict[str, str]) -> set[str]:
    tokens = set(TOKEN_RE.findall(prompt))
    return {t for t in tokens if t not in values}
