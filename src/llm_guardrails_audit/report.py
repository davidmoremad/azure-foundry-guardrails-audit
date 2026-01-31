from __future__ import annotations
import json
import hashlib
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
from .models import CaseResult
from .scoring import summarize_by_risk

def sha256_text(s: str | None) -> str | None:
    if s is None:
        return None
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

def build_report(target: Dict[str, Any], results: List[CaseResult], store_hashes: bool = True) -> Dict[str, Any]:
    summary = summarize_by_risk(results)

    out_cases = []
    for r in results:
        o = r.observed
        case_obj = {
            "case_id": r.case.case_id,
            "risk": r.case.risk,
            "channel": r.case.channel,
            "language": r.case.language,
            "http_status": o.http_status,
            "finish_reason": o.finish_reason,
            "error": o.error,
            "filter_signals": asdict(o.filter_signals),
            "classification": {
                "status": r.classification_status,
                "reason": r.classification_reason,
            },
        }

        if store_hashes:
            case_obj["content_hash"] = o.content
        out_cases.append(case_obj)

    report = {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "summary": {k: {"status": v.status, "evidence": v.evidence} for k, v in summary.items()},
        "cases": out_cases,
    }
    return report

def save_report(report: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
