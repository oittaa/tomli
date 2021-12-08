import json
from pathlib import Path

import pytest

import tomli
from . import burntsushi

DATA_DIR = Path(__file__).parent / "data" / "burntsushi-repo"

VALID_FILES = tuple((DATA_DIR / "valid").glob("**/*.toml"))
VALID_FILES_EXPECTED = tuple(
    json.loads(p.with_suffix(".json").read_bytes().decode()) for p in VALID_FILES
)

INVALID_FILES = tuple((DATA_DIR / "invalid").glob("**/*.toml"))


@pytest.mark.parametrize(
    "invalid",
    INVALID_FILES,
    ids=[p.stem for p in INVALID_FILES],
)
def test_invalid(invalid):
    with pytest.raises(tomli.TOMLDecodeError):
        with open(invalid, "rb") as bin_f:
            tomli.load(bin_f)


@pytest.mark.parametrize(
    "valid,expected",
    zip(VALID_FILES, VALID_FILES_EXPECTED),
    ids=[p.stem for p in VALID_FILES],
)
def test_valid(valid, expected):
    with open(valid, "rb") as bin_f:
        actual = tomli.load(bin_f)
    actual = burntsushi.convert(actual)
    expected = burntsushi.normalize_burntsushi(expected)
    assert actual == expected
