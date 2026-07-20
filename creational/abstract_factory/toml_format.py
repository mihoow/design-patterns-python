"""TOML product family for the Abstract Factory example."""

from __future__ import annotations

import json
import re

from .abstractions import (
    DataFormat,
    DictNode,
    KeyValueNode,
    ListNode,
    RootNode,
    SerializationContext,
)


class TOMLRootNode(RootNode):
    """Represent the root of a TOML document."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize the complete TOML document."""
        current = _context(context)
        return _serialize_entries(self.entries, current.path)


class TOMLKeyValueNode(KeyValueNode):
    """Represent a TOML key-value pair."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a TOML assignment or nested table."""
        current = _context(context)
        path = (*current.path, self.key)
        if isinstance(self.value, TOMLDictNode):
            return self.value.serialize(SerializationContext(path=path))
        if _is_table_array(self.value):
            return self.value.serialize(SerializationContext(path=path))
        value = _serialize_inline(self.value)
        return f"{_key(self.key)} = {value}"


class TOMLDictNode(DictNode):
    """Represent a TOML table."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize a TOML table and its nested tables."""
        current = _context(context)
        header = f"[{_path(current.path)}]"
        body = _serialize_entries(self.entries, current.path)
        return _join_header_and_body(header, body)


class TOMLListNode(ListNode):
    """Represent a TOML array."""

    def serialize(
        self,
        context: SerializationContext | None = None,
    ) -> str:
        """Serialize an inline array or an array of tables."""
        current = _context(context)
        if not _is_table_array(self):
            return _serialize_inline(self)

        blocks = []
        for value in self.values:
            header = f"[[{_path(current.path)}]]"
            body = _serialize_entries(value.entries, current.path)
            blocks.append(_join_header_and_body(header, body))
        return "\n\n".join(blocks)


class TOMLDataFormat(DataFormat):
    """Create a compatible family of TOML nodes."""

    def create_root(self, *entries: KeyValueNode) -> RootNode:
        """Create a TOML root node."""
        return TOMLRootNode(*entries)

    def create_key_value(
        self,
        key: str,
        value: str | DictNode | ListNode,
    ) -> KeyValueNode:
        """Create a TOML key-value node."""
        return TOMLKeyValueNode(key, value)

    def create_dict(self, *entries: KeyValueNode) -> DictNode:
        """Create a TOML dictionary node."""
        return TOMLDictNode(*entries)

    def create_list(
        self,
        *values: str | DictNode | ListNode,
    ) -> ListNode:
        """Create a TOML list node."""
        return TOMLListNode(*values)


def _context(
    context: SerializationContext | None,
) -> SerializationContext:
    return context if context is not None else SerializationContext()


def _key(key: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]+", key):
        return key
    return json.dumps(key, ensure_ascii=False)


def _path(path: tuple[str, ...]) -> str:
    return ".".join(_key(part) for part in path)


def _is_table_array(value: object) -> bool:
    return (
        isinstance(value, TOMLListNode)
        and bool(value.values)
        and all(isinstance(item, TOMLDictNode) for item in value.values)
    )


def _serialize_inline(value: str | DictNode | ListNode) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, ListNode):
        values = ", ".join(_serialize_inline(item) for item in value.values)
        return f"[{values}]"
    if isinstance(value, DictNode):
        entries = ", ".join(
            f"{_key(entry.key)} = {_serialize_inline(entry.value)}"
            for entry in value.entries
        )
        return f"{{ {entries} }}"
    raise TypeError(f"Unsupported TOML value: {type(value).__name__}")


def _serialize_entries(
    entries: tuple[KeyValueNode, ...],
    path: tuple[str, ...],
) -> str:
    assignments = []
    nested_blocks = []
    context = SerializationContext(path=path)
    for entry in entries:
        if isinstance(entry.value, TOMLDictNode) or _is_table_array(
            entry.value
        ):
            nested_blocks.append(entry.serialize(context))
        else:
            assignments.append(entry.serialize(context))

    blocks = []
    if assignments:
        blocks.append("\n".join(assignments))
    blocks.extend(nested_blocks)
    return "\n\n".join(blocks)


def _join_header_and_body(header: str, body: str) -> str:
    return f"{header}\n{body}" if body else header
