from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from app.organization import JsonOrganizationRepository, RegistryError

from .errors import AgentDefinitionError, DefinitionFinding, DefinitionValidationError
from .json_repository import JsonAgentManifestRepository
from .prompt_loader import PromptLoader
from .readiness import evaluate_all, evaluate_readiness
from .service import AgentDefinitionService


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect governed MFI agent definitions.", allow_abbrev=False
    )
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate all Cohort 1 definitions.")
    subparsers.add_parser("summary", help="Show lifecycle and readiness summary.")
    subparsers.add_parser("readiness", help="Show aggregate readiness counts.")
    show = subparsers.add_parser(
        "show", help="Show one joined definition.", allow_abbrev=False
    )
    show.add_argument("agent_id")
    show.add_argument("--with-prompt", action="store_true")
    return parser


def _load(repo_root: Path):
    return AgentDefinitionService(
        JsonOrganizationRepository(repo_root / "config/organization/registry.json"),
        JsonAgentManifestRepository(repo_root / "config/agents/cohort-1"),
        PromptLoader(repo_root),
    ).load_all()


def _show_definition(definition, include_prompt: bool) -> None:
    readiness = evaluate_readiness(definition)
    record = definition.registry_record
    manifest = definition.manifest
    print(f"Agent: {record.id}")
    print(f"Name: {record.display_name}")
    print(f"Purpose: {record.purpose}")
    print(f"Lifecycle: {record.status.value}")
    print(f"Version: {record.version}")
    print(f"Owner: {record.owner_type.value} {record.owner_id}")
    print(f"Definition: {readiness.completeness.value}")
    print(f"Activation: {readiness.eligibility.value}")
    print("Input contracts:")
    for contract in manifest.input_contracts:
        print(f"  {contract.id}: {', '.join(contract.required_fields)}")
    print("Output contracts:")
    for contract in manifest.output_contracts:
        print(f"  {contract.id}: {', '.join(contract.required_fields)}")
    print("Prompt sources:")
    for source in definition.prompt_sources:
        print(f"  {source.path}  sha256={source.sha256_digest}")
    print(f"Tools: {len(manifest.allowed_tools)}")
    print(f"Authority grants: {len(definition.resolved_grants)}")
    print("Blockers:")
    for blocker in readiness.blocker_codes:
        print(f"  {blocker}")
    if include_prompt:
        print("\nComposed prompt:\n")
        print(definition.composed_prompt)


def _safe_diagnostic(text: str) -> str:
    return "".join(
        character if character.isprintable() or character == " " else f"\\x{ord(character):02x}"
        for character in text
    )


def _print_expected_error(error: Exception) -> None:
    findings = getattr(error, "findings", None)
    if findings is not None:
        lines = (str(finding) for finding in findings)
    else:
        lines = str(error).splitlines() or (error.__class__.__name__,)
    for line in lines:
        print(_safe_diagnostic(line), file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        definitions = _load(arguments.repo_root.resolve())
        reports = evaluate_all(definitions)
        report_by_id = {report.agent_id: report for report in reports}

        if arguments.command == "validate":
            prompt_count = sum(len(item.prompt_sources) for item in definitions)
            grant_count = sum(len(item.resolved_grants) for item in definitions)
            print(
                f"{len(definitions)} Cohort 1 definitions valid; "
                f"{prompt_count} prompt sources loaded; "
                f"{grant_count} authority grants resolved."
            )
        elif arguments.command == "summary":
            for definition in definitions:
                record = definition.registry_record
                report = report_by_id[record.id]
                print(
                    f"{record.id:31} {report.completeness.value:8} "
                    f"{record.status.value:7} {report.eligibility.value}"
                )
        elif arguments.command == "readiness":
            complete = sum(report.completeness.value == "COMPLETE" for report in reports)
            eligible = sum(report.eligibility.value == "ELIGIBLE" for report in reports)
            blocked = sum(report.eligibility.value == "BLOCKED" for report in reports)
            print(
                f"{complete} definition-complete; {eligible} activation-eligible; "
                f"{blocked} blocked."
            )
        elif arguments.command == "show":
            definition = next(
                (
                    item
                    for item in definitions
                    if item.registry_record.id == arguments.agent_id
                ),
                None,
            )
            if definition is None:
                raise DefinitionValidationError(
                    (
                        DefinitionFinding(
                            "agent_id", f"unknown agent ID {arguments.agent_id!r}"
                        ),
                    )
                )
            _show_definition(definition, arguments.with_prompt)
        return 0
    except (AgentDefinitionError, RegistryError) as error:
        _print_expected_error(error)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
