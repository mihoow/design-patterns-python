"""Public API for the Prototype example."""

from .repository import JsonRoleRepository
from .roles import (
    ApplicationRole,
    InfrastructureRole,
    Role,
)

__all__ = [
    "ApplicationRole",
    "InfrastructureRole",
    "JsonRoleRepository",
    "Role",
]
