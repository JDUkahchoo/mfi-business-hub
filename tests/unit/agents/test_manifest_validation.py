from __future__ import annotations

from dataclasses import replace

from app.agents.definitions.json_repository import parse_manifest_data
from app.agents.definitions.models import (
    DataClassification,
    ExecutionPolicy,
    FailureAction,
)
from app.agents.definitions.validation import validate_manifest


def _paths_and_messages(manifest) -> tuple[tuple[str, str], ...]:
    return tuple((item.path, item.message) for item in validate_manifest(manifest))


def test_valid_manifest_has_no_semantic_findings(
    valid_manifest_data: dict[str, object],
) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    assert validate_manifest(manifest) == ()


def test_rejects_identity_statements_contracts_and_access_expansion(
    valid_manifest_data: dict[str, object],
) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    manifest = replace(
        manifest,
        agent_id="MFI Orchestrator",
        responsibilities=("", "duplicate", "duplicate"),
        non_responsibilities=(),
        input_contracts=(),
        allowed_tools=("send-email",),
        allowed_systems=("unknown-system",),
        allowed_data_classifications=(DataClassification.CONFIDENTIAL,),
        authority_grant_ids=("grant-extra",),
        prompt_sources=("same.md", "same.md"),
    )

    findings = _paths_and_messages(manifest)
    text = "\n".join(f"{path}: {message}" for path, message in findings)
    assert "agent_id" in text
    assert "responsibilities" in text and "blank" in text and "duplicate" in text
    assert "non_responsibilities" in text
    assert "input_contracts" in text
    assert "allowed_tools" in text
    assert "allowed_systems" in text
    assert "allowed_data_classifications" in text
    assert "authority_grant_ids" in text
    assert "prompt_sources" in text and "duplicate" in text


def test_rejects_invalid_contract_fields_policy_and_audit_set(
    valid_manifest_data: dict[str, object],
) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    bad_contract = replace(
        manifest.input_contracts[0],
        id="Bad ID",
        required_fields=("not-kebab", "not-kebab"),
    )
    bad_failure = replace(
        manifest.failure_behavior,
        on_dependency_failure=FailureAction.STOP_AND_ESCALATE,
        preserve_working_artifacts=False,
    )
    bad_escalation = replace(
        manifest.escalation,
        include_evidence=False,
        conditions=("Missing authority.",),
    )
    manifest = replace(
        manifest,
        input_contracts=(bad_contract,),
        routing_policy=replace(
            manifest.routing_policy,
            execution_policy=ExecutionPolicy.LOCAL_ONLY,
            cloud_fallback_allowed=True,
        ),
        audit_events=("agent.run.requested", "agent.run.extra"),
        failure_behavior=bad_failure,
        escalation=bad_escalation,
    )

    text = "\n".join(
        f"{path}: {message}" for path, message in _paths_and_messages(manifest)
    )
    for fragment in (
        "input_contracts",
        "routing_policy",
        "audit_events",
        "failure_behavior",
        "escalation",
    ):
        assert fragment in text


def test_scans_all_nested_strings_for_normalized_provider_or_model_tokens(
    valid_manifest_data: dict[str, object],
) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    contract = replace(manifest.input_contracts[0], description="Use Ge-mma output.")
    criterion = replace(
        manifest.acceptance_criteria[0], description="Reviewed in Open AI format."
    )
    manifest = replace(
        manifest,
        responsibilities=("Ask CLAUDE for help.",),
        input_contracts=(contract,),
        acceptance_criteria=(criterion,),
    )

    findings = validate_manifest(manifest)

    assert len([item for item in findings if "provider/model" in item.message]) == 3


def test_generic_provider_independent_terms_remain_valid(
    valid_manifest_data: dict[str, object],
) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    manifest = replace(
        manifest,
        responsibilities=("Use an approved provider-independent capability.",),
        non_responsibilities=("Do not choose a local model or cloud model.",),
    )

    assert validate_manifest(manifest) == ()
