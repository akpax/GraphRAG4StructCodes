import pytest
from pytest_unordered import unordered
import pathlib

from ..mine_html import (
    find_item_references,
    find_chapter_references,
    find_id,
    get_chapter_from_path,
    determine_section_or_chapter,
    remove_refs_ending_in_0,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("this is contains no references", []),
        ("3.2.3 this contains 1 reference", ["3.2.3"]),
        ("this contains 1.2.32.3 2 references 9.23.12.1 ", ["1.2.32.3", "9.23.12.1"]),
        ("this contains O REFERENCES 1. ", []),
        ("check duplicates 1.2.3 1.2.3", ["1.2.3"]),
        ("check case where chapter does not exist 0.2.3 this should be excluded", []),
        ("another case where chapter does not exist 28.2.3 should be excluded", []),
        ("exclusion case 1.2.3 should exclude 28.2.3 ", ["1.2.3"]),
        ("testing zero exclusion 5.2.3.0 next ref 1.2.3 ", ["1.2.3"]),
    ],
)
def test_find_item_references(test_input, expected):
    out = find_item_references(test_input)
    assert out == unordered(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Chapter 12", ["12"]),
        ("fluff text Chapter 12 fluff text", ["12"]),
        ("Chapter 12 Chapter 13", ["12", "13"]),
        (
            "multiple chapters Chapter 12 with fluff text Chapter 13 extra fluff",
            ["12", "13"],
        ),
        ("no Chapter reference", []),
        ("check duplicates Chapter 12 Chapter 12", ["12"]),
    ],
)
def test_find_chapter_references(test_input, expected):
    out = find_chapter_references(test_input)
    assert out == unordered(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Chapter 12 this is extra text", "12"),
        ("fluff text Chapter 12 fluff text", None),
        ("Chapter 12 Chapter 13", "12"),
        ("12.3.2 this is extra text", "12.3.2"),
        ("this checks no ID case 12.3.42", None),
        (" 12.3.2.4 check space in begining case", "12.3.2.4"),
    ],
)
def test_find_id(test_input, expected):
    out = find_id(test_input)
    assert out == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("12", "chapter"),
        ("11", "chapter"),
        ("12.1", "section"),
        ("12.3.2", "section"),
    ],
)
def test_determine_section_or_chapter(test_input, expected):
    assert determine_section_or_chapter(test_input) == expected


def test_id_typical_case():
    path = pathlib.Path("data/ACI318-19_html/ACI318-19_ch1.html")
    assert get_chapter_from_path(path) == "ch1"


def test_remove_refs_ending_in_0():
    test = ["1.2.3.0", "2.3.2", "1.2.3.00"]
    assert remove_refs_ending_in_0(test) == ["2.3.2"]
