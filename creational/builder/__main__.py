"""Run the console demonstration for the Builder example."""

from decimal import Decimal
from time import sleep

from .builder import (
    CustomerReceiptBuilder,
    KitchenTicketBuilder,
    OrderProcessor,
    PriceList,
    SandwichRecipe,
)

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
