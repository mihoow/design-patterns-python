"""Tests defining the expected data format behavior."""

from textwrap import dedent

from creational.abstract_factory import (
    DataFormat,
    JSONDataFormat,
    JSONDictNode,
    JSONKeyValueNode,
    JSONListNode,
    JSONRootNode,
    RootNode,
    TOMLDataFormat,
    TOMLDictNode,
    TOMLKeyValueNode,
    TOMLListNode,
    TOMLRootNode,
    YAMLDataFormat,
    YAMLDictNode,
    YAMLKeyValueNode,
    YAMLListNode,
    YAMLRootNode,
)


def create_project_document(factory: DataFormat) -> RootNode:
    """Create the same nested document using any format family."""
    return factory.create_root(
        factory.create_key_value("title", "Design Patterns"),
        factory.create_key_value(
            "categories",
            factory.create_list(
                "creational",
                "structural",
                "behavioral",
            ),
        ),
        factory.create_key_value(
            "maintainers",
            factory.create_list(
                factory.create_dict(
                    factory.create_key_value("name", "Alice"),
                    factory.create_key_value(
                        "roles",
                        factory.create_list("maintainer", "reviewer"),
                    ),
                ),
                factory.create_dict(
                    factory.create_key_value("name", "Bob"),
                    factory.create_key_value(
                        "roles",
                        factory.create_list("contributor"),
                    ),
                ),
            ),
        ),
        factory.create_key_value(
            "repository",
            factory.create_dict(
                factory.create_key_value("provider", "GitHub"),
                factory.create_key_value("owner", "mihoow"),
                factory.create_key_value(
                    "settings",
                    factory.create_dict(
                        factory.create_key_value(
                            "visibility",
                            "public",
                        ),
                        factory.create_key_value("branch", "main"),
                    ),
                ),
            ),
        ),
    )


def test_factories_create_compatible_product_families() -> None:
    """Each factory creates nodes belonging to one format family."""
    json_factory = JSONDataFormat()
    json_value = json_factory.create_key_value("key", "value")
    assert isinstance(json_factory.create_root(json_value), JSONRootNode)
    assert isinstance(json_value, JSONKeyValueNode)
    assert isinstance(json_factory.create_dict(json_value), JSONDictNode)
    assert isinstance(json_factory.create_list("value"), JSONListNode)

    yaml_factory = YAMLDataFormat()
    yaml_value = yaml_factory.create_key_value("key", "value")
    assert isinstance(yaml_factory.create_root(yaml_value), YAMLRootNode)
    assert isinstance(yaml_value, YAMLKeyValueNode)
    assert isinstance(yaml_factory.create_dict(yaml_value), YAMLDictNode)
    assert isinstance(yaml_factory.create_list("value"), YAMLListNode)

    toml_factory = TOMLDataFormat()
    toml_value = toml_factory.create_key_value("key", "value")
    assert isinstance(toml_factory.create_root(toml_value), TOMLRootNode)
    assert isinstance(toml_value, TOMLKeyValueNode)
    assert isinstance(toml_factory.create_dict(toml_value), TOMLDictNode)
    assert isinstance(toml_factory.create_list("value"), TOMLListNode)


def test_serializes_document_as_json() -> None:
    """A JSON family serializes the project document as JSON."""
    document = create_project_document(JSONDataFormat())
    expected = dedent(
        """
        {
          "title": "Design Patterns",
          "categories": [
            "creational",
            "structural",
            "behavioral"
          ],
          "maintainers": [
            {
              "name": "Alice",
              "roles": [
                "maintainer",
                "reviewer"
              ]
            },
            {
              "name": "Bob",
              "roles": [
                "contributor"
              ]
            }
          ],
          "repository": {
            "provider": "GitHub",
            "owner": "mihoow",
            "settings": {
              "visibility": "public",
              "branch": "main"
            }
          }
        }
        """
    ).strip()

    assert document.serialize() == expected


def test_serializes_document_as_yaml() -> None:
    """A YAML family serializes the project document as YAML."""
    document = create_project_document(YAMLDataFormat())
    expected = dedent(
        """
        title: "Design Patterns"
        categories:
          - "creational"
          - "structural"
          - "behavioral"
        maintainers:
          - name: "Alice"
            roles:
              - "maintainer"
              - "reviewer"
          - name: "Bob"
            roles:
              - "contributor"
        repository:
          provider: "GitHub"
          owner: "mihoow"
          settings:
            visibility: "public"
            branch: "main"
        """
    ).strip()

    assert document.serialize() == expected


def test_serializes_document_as_toml() -> None:
    """A TOML family serializes the project document as TOML."""
    document = create_project_document(TOMLDataFormat())
    expected = dedent(
        """
        title = "Design Patterns"
        categories = ["creational", "structural", "behavioral"]

        [[maintainers]]
        name = "Alice"
        roles = ["maintainer", "reviewer"]

        [[maintainers]]
        name = "Bob"
        roles = ["contributor"]

        [repository]
        provider = "GitHub"
        owner = "mihoow"

        [repository.settings]
        visibility = "public"
        branch = "main"
        """
    ).strip()

    assert document.serialize() == expected
