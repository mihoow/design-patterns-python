"""Demonstrate the Builder pattern with a sandwich order."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from time import sleep


@dataclass(frozen=True)
class SandwichRecipe:
    """Describe a sandwich selected by a customer."""

    bread: str
    meat: str
    extras: tuple[str, ...]
    heated: bool

    def __post_init__(self) -> None:
        """Validate that the recipe contains enough ingredients."""
        if not self.bread.strip():
            raise ValueError("A sandwich requires bread.")
        if self.meat == "No meat" and not self.extras:
            raise ValueError(
                "Choose meat or at least one extra ingredient."
            )


@dataclass(frozen=True)
class KitchenTicket:
    """Contain sandwich preparation instructions for kitchen staff."""

    instructions: tuple[str, ...]

    def __str__(self) -> str:
        """Return a printable kitchen ticket."""
        separator = "-" * 32
        body = "\n".join(self.instructions)
        return f"KITCHEN TICKET\n{separator}\n{body}"


@dataclass(frozen=True)
class ReceiptItem:
    """Represent one priced item on a customer receipt."""

    name: str
    price: Decimal


@dataclass(frozen=True)
class CustomerReceipt:
    """Contain priced items for the customer."""

    items: tuple[ReceiptItem, ...]

    def __str__(self) -> str:
        """Return a printable customer receipt."""
        separator = "-" * 32
        rows = [
            f"{item.name:<23}{item.price:>6.2f} PLN" for item in self.items
        ]
        total = sum((item.price for item in self.items), Decimal("0.00"))
        rows.extend((separator, f"{'Total':<23}{total:>6.2f} PLN"))
        return "\n".join(("CUSTOMER RECEIPT", separator, *rows))


@dataclass(frozen=True)
class PriceList:
    """Store prices independently from a sandwich recipe."""

    breads: dict[str, Decimal]
    meats: dict[str, Decimal]
    extras: dict[str, Decimal]
    heating: Decimal


class OrderDocumentBuilder(ABC):
    """Define steps for interpreting a sandwich recipe."""

    @abstractmethod
    def reset(self) -> None:
        """Prepare the builder for a new result."""

    @abstractmethod
    def add_bread(self, bread: str) -> None:
        """Process the selected bread."""

    @abstractmethod
    def add_meat(self, meat: str) -> None:
        """Process the selected meat."""

    @abstractmethod
    def add_extra(self, extra: str) -> None:
        """Process one selected extra."""

    @abstractmethod
    def set_heating(self, heated: bool) -> None:
        """Process the heating preference."""


class KitchenTicketBuilder(OrderDocumentBuilder):
    """Build preparation instructions for kitchen staff."""

    def __init__(self) -> None:
        """Initialize an empty builder."""
        self._instructions: list[str] = []

    def reset(self) -> None:
        """Remove instructions from the previous ticket."""
        self._instructions = []

    def add_bread(self, bread: str) -> None:
        """Add the bread instruction."""
        self._instructions.append(f"Bread: {bread}")

    def add_meat(self, meat: str) -> None:
        """Add the meat instruction."""
        self._instructions.append(f"Meat: {meat}")

    def add_extra(self, extra: str) -> None:
        """Add an extra ingredient instruction."""
        self._instructions.append(f"Add: {extra}")

    def set_heating(self, heated: bool) -> None:
        """Add the final preparation instruction."""
        instruction = "Heat the sandwich" if heated else "Serve cold"
        self._instructions.append(instruction)

    def get_ticket(self) -> KitchenTicket:
        """Return the completed kitchen ticket."""
        return KitchenTicket(tuple(self._instructions))


class CustomerReceiptBuilder(OrderDocumentBuilder):
    """Build a customer receipt using a separate price list."""

    def __init__(self, price_list: PriceList) -> None:
        """Initialize the builder with its price list."""
        self._price_list = price_list
        self._items: list[ReceiptItem] = []

    def reset(self) -> None:
        """Remove items from the previous receipt."""
        self._items = []

    def add_bread(self, bread: str) -> None:
        """Add the selected bread and its price."""
        self._items.append(ReceiptItem(bread, self._price_list.breads[bread]))

    def add_meat(self, meat: str) -> None:
        """Add the selected meat and its price."""
        self._items.append(ReceiptItem(meat, self._price_list.meats[meat]))

    def add_extra(self, extra: str) -> None:
        """Add an extra ingredient and its price."""
        self._items.append(ReceiptItem(extra, self._price_list.extras[extra]))

    def set_heating(self, heated: bool) -> None:
        """Add heating to the receipt when requested."""
        if heated:
            item = ReceiptItem("Heating", self._price_list.heating)
            self._items.append(item)

    def get_receipt(self) -> CustomerReceipt:
        """Return the completed customer receipt."""
        return CustomerReceipt(tuple(self._items))


class OrderProcessor:
    """Direct builders through the sandwich recipe."""

    def __init__(self, builder: OrderDocumentBuilder) -> None:
        """Initialize the director with a concrete builder."""
        self._builder = builder

    def build_document(self, recipe: SandwichRecipe) -> None:
        """Use a builder to interpret every part of a recipe."""
        self._builder.reset()
        self._builder.add_bread(recipe.bread)
        self._builder.add_meat(recipe.meat)
        for extra in recipe.extras:
            self._builder.add_extra(extra)
        self._builder.set_heating(recipe.heated)


BREADS = ("White bread", "Whole wheat bread", "Rye bread")
MEATS = ("Chicken", "Ham", "Beef", "No meat")
EXTRAS = ("Cheese", "Tomato", "Lettuce", "Pickles")

PRICE_LIST = PriceList(
    breads={
        "White bread": Decimal("4.00"),
        "Whole wheat bread": Decimal("4.50"),
        "Rye bread": Decimal("5.00"),
    },
    meats={
        "Chicken": Decimal("5.00"),
        "Ham": Decimal("4.50"),
        "Beef": Decimal("6.50"),
        "No meat": Decimal("0.00"),
    },
    extras={
        "Cheese": Decimal("1.50"),
        "Tomato": Decimal("1.00"),
        "Lettuce": Decimal("1.00"),
        "Pickles": Decimal("1.00"),
    },
    heating=Decimal("0.50"),
)


def choose_one(prompt: str, options: tuple[str, ...]) -> str:
    """Ask the user to choose one option."""
    print(f"\n{prompt}")
    for number, option in enumerate(options, start=1):
        print(f"{number}. {option}")

    while True:
        answer = input("Choice: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Please enter one of the displayed numbers.")


def choose_extras(options: tuple[str, ...]) -> tuple[str, ...]:
    """Ask the user which extras should be included."""
    selected = []
    print("\nChoose extras:")
    for option in options:
        answer = input(f"Add {option}? [y/N]: ").strip().lower()
        if answer == "y":
            selected.append(option)
    return tuple(selected)


def ask_yes_no(prompt: str) -> bool:
    """Ask the user a yes-or-no question."""
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in {"y", "n"}:
            return answer == "y"
        print("Please enter 'y' or 'n'.")


def collect_recipe() -> SandwichRecipe:
    """Collect an individual sandwich recipe from the customer."""
    bread = choose_one("Choose bread:", BREADS)
    meat = choose_one("Choose meat:", MEATS)
    extras = choose_extras(EXTRAS)
    while meat == "No meat" and not extras:
        print("Choose at least one extra for a meat-free sandwich.")
        extras = choose_extras(EXTRAS)
    heated = ask_yes_no("Heat the sandwich?")
    return SandwichRecipe(bread, meat, extras, heated)


def wait_for_sandwich() -> None:
    """Display a short preparation indicator."""
    print("\nPreparing sandwich", end="", flush=True)
    for _ in range(4):
        sleep(0.5)
        print(".", end="", flush=True)
    print(" done!\n")


def main() -> None:
    """Run the interactive sandwich shop example."""
    print("Welcome to the sandwich shop!")
    recipe = collect_recipe()

    ticket_builder = KitchenTicketBuilder()
    processor = OrderProcessor(ticket_builder)
    processor.build_document(recipe)
    print(f"\n{ticket_builder.get_ticket()}")

    wait_for_sandwich()

    receipt_builder = CustomerReceiptBuilder(PRICE_LIST)
    processor = OrderProcessor(receipt_builder)
    processor.build_document(recipe)
    print(receipt_builder.get_receipt())


if __name__ == "__main__":
    main()
