from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Literal, Dict, List

Risk = Literal[
    "jailbreak",
    "hate",
    "self_harm",
    "sexual",
    "violence",
    "protected_material_code",
    "protected_material_text",
]

Channel = Literal["input", "output"]

GuardrailStatus = Literal["ON_BLOCKING", "ON_ANNOTATE_ONLY", "OFF", "INCONCLUSIVE"]
BlockLayer = Literal["platform", "content_filter", "model", "none", "inconclusive"]

@dataclass(frozen=True)
class Case:
    case_id: str
    risk: Risk
    channel: Channel
    language: str
    prompt: str
    goal: Optional[str] = None  # optional human explanation

@dataclass
class RequestParams:
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 200
    timeout_s: int = 30
    retries: int = 2
    retry_backoff_s: float = 1.5

@dataclass
class FilterSignals:
    annotations_present: bool = False
    finish_reason: Optional[str] = None
    blocked: bool = False

    # New: store per-category metadata as returned by the service
    # Example:
    # categories["hate"] = {"filtered": false, "severity":"safe"}
    categories: Dict[str, Dict[str, object]] | None = None

    # Optional detectors
    jailbreak_detected: Optional[bool] = None
    protected_material_text: Optional[bool] = None
    protected_material_code: Optional[bool] = None

    raw: Dict[str, Any] | None = None

@dataclass
class ObservedResponse:
    http_status: int
    content: Optional[str]
    finish_reason: Optional[str]
    error: Optional[str]
    filter_signals: FilterSignals
    headers: Dict[str, str] | None = None
    raw_json: Any | None = None

    # Derived at runtime; you can avoid storing full content by storing only this boolean.
    model_refused: bool = False

@dataclass
class CaseClassification:
    guardrail_status: GuardrailStatus
    block_layer: BlockLayer
    evidence_codes: List[str]
    reason: str

@dataclass
class CaseResult:
    case: Case
    params: RequestParams
    observed: ObservedResponse
    classification: CaseClassification

@dataclass
class RiskSummary:
    risk: Risk
    guardrail_status: GuardrailStatus
    classifier_visible: bool
    platform_block_observed: bool
    model_refusal_observed: bool
    evidence: List[str]
