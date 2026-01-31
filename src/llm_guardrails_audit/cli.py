from __future__ import annotations
import os
import sys
import yaml
from dotenv import load_dotenv
from .pack_loader import load_pack
from .placeholders import load_placeholders
from .models import RequestParams
from .azure_client import AzureOpenAIClient
from .runner import run_cases
from .report import build_report, save_report

def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def main() -> int:
    load_dotenv()

    # Convention over config:
    pack_path = os.environ.get("AUDIT_PACK", "packs/core_pack.yaml")
    placeholders_path = os.environ.get("AUDIT_PLACEHOLDERS", "packs/placeholders.local.yaml")
    target_cfg_path = os.environ.get("AUDIT_TARGET", "configs/target.example.yaml")
    run_cfg_path = os.environ.get("AUDIT_RUNCFG", "configs/run.defaults.yaml")
    out_path = os.environ.get("AUDIT_OUT", "reports/report.json")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    target_cfg = _load_yaml(target_cfg_path)
    run_cfg = _load_yaml(run_cfg_path)

    params = RequestParams(**run_cfg.get("request", {}))
    store_hashes = bool(run_cfg.get("logging", {}).get("store_output_hash", True))

    endpoint = os.environ[target_cfg["endpoint_env"]]
    api_key = os.environ[target_cfg["api_key_env"]]
    api_version = os.environ[target_cfg["api_version_env"]]
    deployment = os.environ[target_cfg["deployment_env"]]

    client = AzureOpenAIClient(endpoint, api_key, api_version, deployment)

    cases = load_pack(pack_path)
    placeholders = load_placeholders(placeholders_path) if os.path.exists(placeholders_path) else {}

    results = run_cases(client, cases, params, placeholders)

    target = {
        "provider": target_cfg.get("provider", "azure_openai"),
        "endpoint": endpoint,
        "deployment": deployment,
        "api_version": api_version,
    }

    report = build_report(target, results, store_hashes=store_hashes)
    save_report(report, out_path)

    # Console summary
    print("\n=== Guardrails Audit Summary (v2) ===")
    for risk, item in report["summary"].items():
        print(
            f"- {risk}: guardrail={item['guardrail_status']} "
            f"classifier={item['classifier_visible']} "
            f"platform_block={item['platform_block_observed']} "
            f"model_refusal={item['model_refusal_observed']} "
            f"evidence={item['evidence']}"
        )
    print(f"\nSaved report: {out_path}\n")


if __name__ == "__main__":
    raise SystemExit(main())
