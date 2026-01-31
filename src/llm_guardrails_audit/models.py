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
Status = Literal["ON_BLOCKING", "ON_ANNOTATE_ONLY", "OFF", "INCONCLUSIVE"]

@dataclass(frozen=True)
class Case:
    case_id: str
    risk: Risk
    channel: Channel
    language: str
    prompt: str

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

    # NEW: per-category details
    categories: Dict[str, Dict[str, object]] | None = None
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

@dataclass
class CaseResult:
    case: Case
    params: RequestParams
    observed: ObservedResponse
    classification_status: Status
    classification_reason: str

@dataclass
class RiskSummary:
    risk: Risk
    status: Status
    evidence: List[str]
