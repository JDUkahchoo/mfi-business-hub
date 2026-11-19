from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from .errors import RegistryLoadError, RegistryValidationError
from .json_repository import JsonOrganizationRepository

DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "organization" / "registry.json"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the MFI organization registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "summary"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument(
            "--registry",
            type=Path,
            default=DEFAULT_REGISTRY_PATH,
            help="Path to the organization registry JSON file.",
        )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        registry = JsonOrganizationRepository(arguments.registry).load()
    except RegistryValidationError as error:
        for finding in error.findings:
            print(f"error: {finding}", file=sys.stderr)
        return 2
    except RegistryLoadError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if arguments.command == "validate":
        print("Registry valid.")
    else:
        print(
            "Registry valid: "
            f"{len(registry.roles)} roles, "
            f"{len(registry.seats)} seats, "
            f"{len(registry.agents)} agents, "
            f"{len(registry.authority_grants)} authority grants."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
