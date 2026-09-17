from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType


def load_effects_table(
    path: Path, enum_cls: type, valid_stats: Iterable[str]
) -> Mapping[object, Mapping[str, int]]:
    """Load a `{enum value: {stat: delta}}` JSON file, validated against
    `enum_cls`'s values and `valid_stats`, into the same nested
    MappingProxyType shape the code previously defined as a literal."""
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)

    expected_keys = {member.value for member in enum_cls}
    actual_keys = set(raw)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        unknown = sorted(actual_keys - expected_keys)
        raise ValueError(
            f"{path}: keys must exactly match {enum_cls.__name__} values "
            f"(missing={missing}, unknown={unknown})"
        )

    known_stats = set(valid_stats)
    table: dict[object, Mapping[str, int]] = {}
    for key, effects in raw.items():
        unknown_stats = sorted(set(effects) - known_stats)
        if unknown_stats:
            raise ValueError(f"{path}: unknown stats for {key!r}: {unknown_stats}")
        table[enum_cls(key)] = MappingProxyType(dict(effects))

    return MappingProxyType(table)
