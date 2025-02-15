import json
from pathlib import Path

import pytest

import tomli
from . import burntsushi


class MissingFile:
    def __init__(self, path: Path):
        self.path = path


DATA_DIR = Path(__file__).parent / "data" / "toml-lang-compliance"

VALID_FILES = tuple((DATA_DIR / "valid").glob("**/*.toml"))
# VALID_FILES_EXPECTED = tuple(
#     json.loads(p.with_suffix(".json").read_bytes().decode()) for p in VALID_FILES
# )
_expected_files = []
for p in VALID_FILES:
    json_path = p.with_suffix(".json")
    try:
        text = json.loads(json_path.read_bytes().decode())
    except FileNotFoundError:
        text = MissingFile(json_path)
    _expected_files.append(text)

VALID_FILES_EXPECTED = tuple(_expected_files)
INVALID_FILES = tuple((DATA_DIR / "invalid").glob("**/*.toml"))


@pytest.mark.parametrize(
    "invalid",
    INVALID_FILES,
    ids=[p.stem for p in INVALID_FILES],
)
def test_invalid(invalid):
    toml_str = invalid.read_bytes().decode()
    with pytest.raises(tomli.TOMLDecodeError):
        tomli.loads(toml_str)


@pytest.mark.parametrize(
    "valid,expected",
    zip(VALID_FILES, VALID_FILES_EXPECTED),
    ids=[p.stem for p in VALID_FILES],
)
def test_valid(valid, expected):
    toml_str = valid.read_bytes().decode()
    actual = tomli.loads(toml_str)
    if isinstance(expected, MissingFile):
        assert isinstance(actual, dict)
        pytest.xfail(f"Missing a .json file corresponding the .toml: {expected.path}")
    actual = burntsushi.convert(actual)
    expected = burntsushi.normalize(expected)
    assert actual == expected
