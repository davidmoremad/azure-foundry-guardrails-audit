from __future__ import annotations
import time
from typing import List, Dict
from .models import Case, RequestParams, CaseResult, ObservedResponse, FilterSignals
from .placeholders import apply_placeholders, find_missing
from .scoring import detect_model_refusal, classify_case

def run_cases(client, cases: List[Case], params: RequestParams, placeholders: Dict[str, str]) -> List[CaseResult]:
    results: List[CaseResult] = []

    for c in cases:
        prompt = apply_placeholders(c.prompt, placeholders)
        missing = find_missing(c.prompt, placeholders)
        if missing:
            observed = ObservedResponse(
                http_status=0,
                content=None,
                finish_reason=None,
                error=f"Missing placeholders: {sorted(missing)}",
                filter_signals=FilterSignals(),
                headers=None,
                raw_json=None,
                model_refused=False,
            )
            dummy = CaseResult(
                case=c,
                params=params,
                observed=observed,
                classification=None,  # fill below
            )
            classification = classify_case(dummy)  # will become OFF/none w/out signals; override as inconclusive
            classification.guardrail_status = "INCONCLUSIVE"
            classification.block_layer = "inconclusive"
            classification.evidence_codes = ["TEST_NOT_EXECUTED_MISSING_PLACEHOLDERS"]
            classification.reason = "Missing placeholders; case not executed."
            dummy.classification = classification
            results.append(dummy)
            continue

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
            last_obs = ObservedResponse(
                http_status=0,
                content=None,
                finish_reason=None,
                error=err or "Unknown error",
                filter_signals=FilterSignals(),
                headers=None,
                raw_json=None,
                model_refused=False,
            )

        # Derive model refusal boolean (you can later avoid storing content entirely)
        last_obs.model_refused = detect_model_refusal(last_obs.content)

        tmp = CaseResult(
            case=c,
            params=params,
            observed=last_obs,
            classification=None,
        )
        tmp.classification = classify_case(tmp)
        results.append(tmp)

    return results
