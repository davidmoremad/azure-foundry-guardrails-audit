from __future__ import annotations
import time
from typing import List, Dict
from .models import Case, RequestParams, CaseResult
from .placeholders import apply_placeholders, find_missing
from .scoring import classify_case

def run_cases(client, cases: List[Case], params: RequestParams, placeholders: Dict[str, str]) -> List[CaseResult]:
    results: List[CaseResult] = []

    for c in cases:
        prompt = apply_placeholders(c.prompt, placeholders)
        missing = find_missing(c.prompt, placeholders)
        if missing:
            # Keep execution deterministic: mark inconclusive; do not call model
            from .models import ObservedResponse, FilterSignals
            observed = ObservedResponse(
                http_status=0,
                content=None,
                finish_reason=None,
                error=f"Missing placeholders: {sorted(missing)}",
                filter_signals=FilterSignals(),
                headers=None,
                raw_json=None,
            )
            cr = CaseResult(
                case=c,
                params=params,
                observed=observed,
                classification_status="INCONCLUSIVE",
                classification_reason="Missing placeholders; case not executed",
            )
            results.append(cr)
            continue

        # basic retry loop
        last_obs = None
        err = None
        for attempt in range(params.retries + 1):
            try:
                last_obs = client.chat_completions(prompt, params)
                err = None
                break
            except Exception as e:
                err = str(e)
                time.sleep(params.retry_backoff_s * (attempt + 1))

        if last_obs is None:
            from .models import ObservedResponse, FilterSignals
            last_obs = ObservedResponse(
                http_status=0,
                content=None,
                finish_reason=None,
                error=err or "Unknown error",
                filter_signals=FilterSignals(),
                headers=None,
                raw_json=None,
            )

        cr = CaseResult(
            case=c,
            params=params,
            observed=last_obs,
            classification_status="INCONCLUSIVE",
            classification_reason="",
        )
        status, reason, _ = classify_case(cr)
        cr.classification_status = status
        cr.classification_reason = reason
        results.append(cr)

    return results
