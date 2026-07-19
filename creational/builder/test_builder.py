"""Unit tests for the Builder pattern example."""

from decimal import Decimal

from creational.builder.builder import (
    CustomerReceiptBuilder,
    KitchenTicketBuilder,
    OrderProcessor,
    PriceList,
    ReceiptItem,
    SandwichRecipe,
)


def test_processor_builds_kitchen_ticket() -> None:
    """The kitchen builder creates preparation instructions."""
    recipe = SandwichRecipe("Rye bread", "Chicken", ("Cheese",), True)
    builder = KitchenTicketBuilder()

    OrderProcessor(builder).build_document(recipe)

    assert builder.get_ticket().instructions == (
        "Bread: Rye bread",
        "Meat: Chicken",
        "Add: Cheese",
        "Heat the sandwich",
    )


def test_processor_builds_customer_receipt() -> None:
    """The receipt builder uses its own prices for the recipe."""
    price_list = PriceList(
        breads={"Rye bread": Decimal("5.00")},
        meats={"Chicken": Decimal("6.00")},
        extras={"Cheese": Decimal("1.50")},
        heating=Decimal("0.50"),
    )
    recipe = SandwichRecipe("Rye bread", "Chicken", ("Cheese",), True)
    builder = CustomerReceiptBuilder(price_list)

    OrderProcessor(builder).build_document(recipe)

    assert builder.get_receipt().items == (
        ReceiptItem("Rye bread", Decimal("5.00")),
        ReceiptItem("Chicken", Decimal("6.00")),
        ReceiptItem("Cheese", Decimal("1.50")),
        ReceiptItem("Heating", Decimal("0.50")),
    )
    assert "Total                   13.00 PLN" in str(builder.get_receipt())


def test_processor_resets_builder_before_reuse() -> None:
    """A reused builder does not retain a previous recipe."""
    builder = KitchenTicketBuilder()
    processor = OrderProcessor(builder)
    first_recipe = SandwichRecipe("Rye bread", "Chicken", (), False)
    second_recipe = SandwichRecipe(
        "Rye bread",
        "No meat",
        ("Cheese",),
        False,
    )

    processor.build_document(first_recipe)
    processor.build_document(second_recipe)

    assert "Meat: Chicken" not in builder.get_ticket().instructions
    assert "Meat: No meat" in builder.get_ticket().instructions
