"""Load polymorphic IAM role prototypes from JSON."""

import json
from pathlib import Path
from typing import Any

from .roles import ApplicationRole, InfrastructureRole, Role


class JsonRoleRepository:
    """Retrieve role prototypes stored in a JSON document."""

    def __init__(self, source: Path) -> None:
        """Initialize the repository with its JSON source."""
        self._source = source

    def retrieve_names(self) -> tuple[str, ...]:
        """Return the names of all available role prototypes."""
        return tuple(role_data["name"] for role_data in self._read_roles())

    def retrieve(self, name: str) -> Role:
        """Map the named JSON definition to a concrete role."""
        for role_data in self._read_roles():
            if role_data["name"] == name:
                return self._map_role(role_data)
        raise KeyError(f"Unknown role: {name}")

    def _read_roles(self) -> list[dict[str, Any]]:
        with self._source.open(encoding="utf-8") as source_file:
            document = json.load(source_file)
        return document["roles"]

    def _map_role(self, role_data: dict[str, Any]) -> Role:
        role_type = role_data["type"]
        common_data = {
            "region": role_data["region"],
            "requires_mfa": role_data["requires_mfa"],
            "max_session_minutes": role_data["max_session_minutes"],
        }
        if role_type == "application":
            role = ApplicationRole(**common_data)
            for application, entitlements in role_data["entitlements"].items():
                role.set_entitlements(application, set(entitlements))
            return role
        if role_type == "infrastructure":
            role = InfrastructureRole(**common_data)
            for resource, actions in role_data["resource_actions"].items():
                role.set_resource_actions(resource, set(actions))
            return role
        raise ValueError(f"Unsupported role type: {role_type}")
