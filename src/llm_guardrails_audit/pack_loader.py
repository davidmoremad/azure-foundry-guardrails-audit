from __future__ import annotations
import yaml
from typing import List
from .models import Case

def load_pack(path: str) -> List[Case]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    cases = []
    for item in data.get("cases", []):
        cases.append(
            Case(
                case_id=item["case_id"],
                risk=item["risk"],
                channel=item["channel"],
                language=item.get("language", "en"),
                prompt=item["prompt"],
            )
        )
    return cases
