"""Tests defining the expected IAM role prototype behavior."""

from json import dumps
from pathlib import Path

import pytest

from creational.prototype import (
    ApplicationRole,
    InfrastructureRole,
    JsonRoleRepository,
)
from creational.prototype.__main__ import IAMAdministrator

ROLE_FILE = Path(__file__).with_name("roles.json")


@pytest.fixture
def repository() -> JsonRoleRepository:
    """Return a repository backed by the example role definitions."""
    return JsonRoleRepository(ROLE_FILE)


def test_repository_maps_json_to_concrete_role_types(
    repository: JsonRoleRepository,
) -> None:
    """Role data is mapped to the appropriate concrete prototypes."""
    application_role = repository.retrieve("Payroll Specialist")
    infrastructure_role = repository.retrieve("Cloud Support Operator")

    assert isinstance(application_role, ApplicationRole)
    assert isinstance(infrastructure_role, InfrastructureRole)


def test_application_role_clone_is_independent(
    repository: JsonRoleRepository,
) -> None:
    """Changing an application role clone leaves its prototype unchanged."""
    prototype = repository.retrieve("Payroll Specialist")
    clone = prototype.clone()

    assert isinstance(clone, ApplicationRole)
    clone.set_entitlements("Payroll", {"view-payroll"})

    assert clone is not prototype
    assert clone.entitlements["Payroll"] == {"view-payroll"}
    assert prototype.entitlements["Payroll"] == {
        "approve-payroll",
        "edit-payroll",
        "view-payroll",
    }


def test_infrastructure_role_clone_is_independent(
    repository: JsonRoleRepository,
) -> None:
    """Changing an infrastructure clone leaves its prototype unchanged."""
    prototype = repository.retrieve("Cloud Support Operator")
    clone = prototype.clone()

    assert isinstance(clone, InfrastructureRole)
    clone.set_resource_actions("production/eu/*", {"read"})

    assert clone is not prototype
    assert clone.resource_actions["production/eu/*"] == {"read"}
    assert prototype.resource_actions["production/eu/*"] == {
        "read",
        "restart",
    }


def test_common_setters_are_fluent(
    repository: JsonRoleRepository,
) -> None:
    """Common role restrictions can be chained on any role clone."""
    prototype = repository.retrieve("Payroll Specialist")
    clone = (
        prototype.clone()
        .set_require_mfa(True)
        .set_max_session_minutes(60)
        .set_region("Poland")
    )

    assert clone.requires_mfa is True
    assert clone.max_session_minutes == 60
    assert clone.region == "Poland"
    assert prototype.requires_mfa is False
    assert prototype.max_session_minutes is None
    assert prototype.region is None


def test_multiple_regional_clones_are_independent(
    repository: JsonRoleRepository,
) -> None:
    """One secured prototype can produce independent regional roles."""
    base_role = repository.retrieve("Cloud Support Operator")
    secured_prototype = (
        base_role.clone().set_require_mfa(True).set_max_session_minutes(60)
    )

    administrator = IAMAdministrator(secured_prototype)
    polish_role, german_role = administrator.regionalize_roles(
        ("Poland", "Germany")
    )

    assert polish_role.region == "Poland"
    assert german_role.region == "Germany"
    assert secured_prototype.region is None
    assert base_role.requires_mfa is False


def test_repository_rejects_missing_security_configuration(
    tmp_path: Path,
) -> None:
    """Missing security fields do not silently receive weak defaults."""
    source = tmp_path / "roles.json"
    source.write_text(
        dumps(
            {
                "roles": [
                    {
                        "name": "Incomplete role",
                        "type": "application",
                        "entitlements": {},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    repository = JsonRoleRepository(source)

    with pytest.raises(KeyError, match="region"):
        repository.retrieve("Incomplete role")
