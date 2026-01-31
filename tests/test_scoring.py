from llm_guardrails_audit.models import Case, RequestParams, ObservedResponse, FilterSignals, CaseResult
from llm_guardrails_audit.scoring import classify_case

def test_http_400_is_blocking():
    c = Case("X", "hate", "input", "en", "p")
    obs = ObservedResponse(400, None, None, "blocked", FilterSignals(blocked=True), None, {})
    cr = CaseResult(c, RequestParams(), obs, "INCONCLUSIVE", "")
    status, _, _ = classify_case(cr)
    assert status == "ON_BLOCKING"

def test_annotations_only():
    c = Case("X", "hate", "output", "en", "p")
    obs = ObservedResponse(200, "ok", "stop", None, FilterSignals(annotations_present=True, blocked=False), None, {})
    cr = CaseResult(c, RequestParams(), obs, "INCONCLUSIVE", "")
    status, _, _ = classify_case(cr)
    assert status == "ON_ANNOTATE_ONLY"
