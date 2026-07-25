"""Run the console demonstration for the Prototype example."""

from dataclasses import asdict
from json import dumps
from pathlib import Path

from .repository import JsonRoleRepository
from .roles import Role

ROLE_FILE = Path(__file__).with_name("roles.json")
SESSION_LIMIT_MINUTES = 60


class IAMAdministrator:
    """Create regional variants from an IAM role prototype."""

    def __init__(self, role: Role) -> None:
        """Initialize the administrator with a role prototype."""
        self.role = role

    def regionalize_roles(
        self,
        regions: tuple[str, ...],
    ) -> tuple[Role, ...]:
        """Clone the prototype independently for every region."""
        return tuple(
            self.role.clone().set_region(region) for region in regions
        )


def choose_role(
    repository: JsonRoleRepository,
) -> tuple[str, Role]:
    """Ask the IAM administrator to choose a role prototype."""
    names = repository.retrieve_names()
    print("Available role prototypes:")
    for number, name in enumerate(names, start=1):
        print(f"{number}. {name}")

    while True:
        answer = input("Choose a role: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            name = names[int(answer) - 1]
            return name, repository.retrieve(name)
        print("Please enter one of the displayed numbers.")


def read_regions() -> tuple[str, ...]:
    """Ask which regional role variants should be created."""
    while True:
        answer = input(
            "Enter regions separated by commas "
            "(for example: Poland, Germany): "
        )
        regions = tuple(
            dict.fromkeys(
                region.strip()
                for region in answer.split(",")
                if region.strip()
            )
        )
        if regions:
            return regions
        print("Enter at least one region.")


def print_role(name: str, role: Role) -> None:
    """Print a role without adding console concerns to domain classes."""
    role_data = {
        "name": name,
        "role_type": type(role).__name__,
        **asdict(role),
    }
    print(
        dumps(
            role_data,
            default=sorted,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
    )


def main() -> None:
    """Create secured regional roles from a selected prototype."""
    repository = JsonRoleRepository(ROLE_FILE)
    role_name, base_role = choose_role(repository)

    print("\nRole retrieved from the IAM repository:")
    print_role(role_name, base_role)
    print("\n")

    regions = read_regions()

    secured_prototype = base_role.clone()
    secured_prototype.set_require_mfa(True).set_max_session_minutes(
        SESSION_LIMIT_MINUTES
    )
    administrator = IAMAdministrator(secured_prototype)
    regional_roles = administrator.regionalize_roles(regions)

    print("\nCreated regional roles:")
    for regional_role in regional_roles:
        print()
        print_role(f"{regional_role.region} {role_name}", regional_role)

    print(
        "\nCompany policy: every new regional role requires MFA "
        f"and has a {SESSION_LIMIT_MINUTES}-minute session limit."
    )


if __name__ == "__main__":
    main()
