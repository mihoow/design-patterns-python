"""Run the console demonstration for the Abstract Factory example."""

from . import JSONDataFormat, TOMLDataFormat, YAMLDataFormat


def main() -> None:
    """Serialize a book using all product families."""
    formats = (
        ("JSON", JSONDataFormat()),
        ("YAML", YAMLDataFormat()),
        ("TOML", TOMLDataFormat()),
    )
    for name, factory in formats:
        document = factory.create_root(
            factory.create_key_value(
                "title",
                "Design Patterns: Elements of Reusable "
                "Object-Oriented Software",
            ),
            factory.create_key_value(
                "authors",
                factory.create_list(
                    factory.create_dict(
                        factory.create_key_value(
                            "name",
                            "Erich Gamma",
                        ),
                    ),
                    factory.create_dict(
                        factory.create_key_value(
                            "name",
                            "Richard Helm",
                        ),
                    ),
                    factory.create_dict(
                        factory.create_key_value(
                            "name",
                            "Ralph Johnson",
                        ),
                    ),
                    factory.create_dict(
                        factory.create_key_value(
                            "name",
                            "John Vlissides",
                        ),
                    ),
                ),
            ),
            factory.create_key_value(
                "topics",
                factory.create_list(
                    "creational patterns",
                    "structural patterns",
                    "behavioral patterns",
                ),
            ),
            factory.create_key_value(
                "publication",
                factory.create_dict(
                    factory.create_key_value(
                        "publisher",
                        "Addison-Wesley",
                    ),
                    factory.create_key_value("year", "1994"),
                    factory.create_key_value(
                        "identifiers",
                        factory.create_dict(
                            factory.create_key_value(
                                "isbn_10",
                                "0-201-63361-2",
                            ),
                            factory.create_key_value(
                                "isbn_13",
                                "978-0-201-63361-0",
                            ),
                        ),
                    ),
                ),
            ),
            factory.create_key_value(
                "editions",
                factory.create_list(
                    factory.create_dict(
                        factory.create_key_value("format", "hardcover"),
                        factory.create_key_value("language", "English"),
                    ),
                    factory.create_dict(
                        factory.create_key_value("format", "ebook"),
                        factory.create_key_value("language", "English"),
                    ),
                ),
            ),
        )
        print(f"{name}\n{'-' * len(name)}")
        print(document.serialize(), end="\n\n")


if __name__ == "__main__":
    main()
