"""Define polymorphic IAM role prototypes."""

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Self


@dataclass
class Role(ABC):
    """Define the prototype and common IAM role restrictions."""

    region: str | None
    requires_mfa: bool
    max_session_minutes: int | None

    @abstractmethod
    def clone(self) -> Self:
        """Create an independent copy preserving the concrete role type."""

    def set_region(self, region: str | None) -> Self:
        """Set or remove the regional restriction."""
        if region is not None and not region.strip():
            raise ValueError("Region cannot be blank.")
        self.region = region
        return self

    def set_require_mfa(self, required: bool) -> Self:
        """Set whether multi-factor authentication is required."""
        self.requires_mfa = required
        return self

    def set_max_session_minutes(self, minutes: int | None) -> Self:
        """Set or remove the maximum session duration."""
        if minutes is not None and minutes <= 0:
            raise ValueError("Session duration must be positive.")
        self.max_session_minutes = minutes
        return self


@dataclass
class ApplicationRole(Role):
    """Represent entitlements granted by business applications."""

    entitlements: dict[str, set[str]] = field(default_factory=dict)

    def clone(self) -> Self:
        """Create an independent application role."""
        return deepcopy(self)

    def set_entitlements(
        self,
        application: str,
        entitlements: set[str],
    ) -> Self:
        """Set the complete entitlement set for an application."""
        if not application.strip():
            raise ValueError("Application cannot be blank.")
        self.entitlements[application] = set(entitlements)
        return self


@dataclass
class InfrastructureRole(Role):
    """Represent actions allowed on infrastructure resources."""

    resource_actions: dict[str, set[str]] = field(default_factory=dict)

    def clone(self) -> Self:
        """Create an independent infrastructure role."""
        return deepcopy(self)

    def set_resource_actions(
        self,
        resource_pattern: str,
        actions: set[str],
    ) -> Self:
        """Set the complete action set for a resource pattern."""
        if not resource_pattern.strip():
            raise ValueError("Resource pattern cannot be blank.")
        self.resource_actions[resource_pattern] = set(actions)
        return self
