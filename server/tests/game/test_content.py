import json
from enum import Enum

import pytest

from app.game.content import load_effects_table


class Color(str, Enum):
    RED = "red"
    BLUE = "blue"


VALID_STATS = ("health", "stress")


def write_json(path, data):
    path.write_text(json.dumps(data))
    return path


def test_loads_a_valid_file(tmp_path):
    path = write_json(
        tmp_path / "colors.json",
        {"red": {"health": 1}, "blue": {"stress": -2}},
    )

    table = load_effects_table(path, Color, VALID_STATS)

    assert table[Color.RED] == {"health": 1}
    assert table[Color.BLUE] == {"stress": -2}


def test_raises_when_an_enum_value_is_missing(tmp_path):
    path = write_json(tmp_path / "colors.json", {"red": {"health": 1}})

    with pytest.raises(ValueError, match="missing"):
        load_effects_table(path, Color, VALID_STATS)


def test_raises_when_the_file_has_an_unknown_key(tmp_path):
    path = write_json(
        tmp_path / "colors.json",
        {"red": {"health": 1}, "blue": {"stress": -2}, "green": {"health": 1}},
    )

    with pytest.raises(ValueError, match="unknown"):
        load_effects_table(path, Color, VALID_STATS)


def test_raises_when_an_effect_targets_an_unknown_stat(tmp_path):
    path = write_json(
        tmp_path / "colors.json",
        {"red": {"charisma": 1}, "blue": {"stress": -2}},
    )

    with pytest.raises(ValueError, match="charisma"):
        load_effects_table(path, Color, VALID_STATS)


def test_result_is_read_only(tmp_path):
    path = write_json(
        tmp_path / "colors.json",
        {"red": {"health": 1}, "blue": {"stress": -2}},
    )

    table = load_effects_table(path, Color, VALID_STATS)

    with pytest.raises(TypeError):
        table[Color.RED] = {}
    with pytest.raises(TypeError):
        table[Color.RED]["health"] = 99
