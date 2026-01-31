from __future__ import annotations
from typing import Any, Optional, Dict
from .models import FilterSignals

def parse_signals(http_status: int, raw_json: Any, finish_reason: Optional[str] = None) -> FilterSignals:
    s = FilterSignals()
    s.finish_reason = finish_reason

    # Heurísticas fuertes
    if http_status == 400:
        s.blocked = True
    if finish_reason and "content_filter" in finish_reason:
        s.blocked = True

    try:
        if not (isinstance(raw_json, dict) and "choices" in raw_json and raw_json["choices"]):
            return s

        choice0 = raw_json["choices"][0]
        cfr = choice0.get("content_filter_results") or choice0.get("content_filter_result")
        if cfr is None or not isinstance(cfr, dict):
            return s

        s.annotations_present = True
        s.raw = {"content_filter_results": cfr}
        s.categories = {}

        # Store all known category blocks verbatim
        for key, val in cfr.items():
            if isinstance(val, dict):
                s.categories[key] = dict(val)

        # Normalize jailbreak/protected signals if present
        for jk in ("jailbreak", "prompt_injection"):
            if jk in cfr and isinstance(cfr[jk], dict):
                s.jailbreak_detected = bool(cfr[jk].get("filtered") or cfr[jk].get("detected"))

        if "protected_material_text" in cfr and isinstance(cfr["protected_material_text"], dict):
            s.protected_material_text = bool(cfr["protected_material_text"].get("filtered") or cfr["protected_material_text"].get("detected"))
            if cfr["protected_material_text"].get("filtered") is True:
                s.blocked = True

        if "protected_material_code" in cfr and isinstance(cfr["protected_material_code"], dict):
            s.protected_material_code = bool(cfr["protected_material_code"].get("filtered") or cfr["protected_material_code"].get("detected"))
            if cfr["protected_material_code"].get("filtered") is True:
                s.blocked = True

        # If any harm category says filtered:true => blocked
        for k in ("hate", "self_harm", "sexual", "violence"):
            if k in cfr and isinstance(cfr[k], dict) and cfr[k].get("filtered") is True:
                s.blocked = True

    except Exception:
        pass

    return s
