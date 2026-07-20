"""Demonstrate the Builder pattern with a sandwich order."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


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
            raise ValueError("Choose meat or at least one extra ingredient.")


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
