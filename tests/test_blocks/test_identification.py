import pytest
from wynntilsresolver.blocks.identification import Identification, estimate_internal_roll


@pytest.mark.parametrize(
    ("base", "value", "perfect", "inverted", "expected"),
    [
        # positive base: roll range 30-130, roll closest to value / base
        (40, 26, False, False, 65),
        (5, 6, False, False, 120),
        # value implies a roll above 130, clamped into the range but kept off the perfect roll
        (15, 20, False, False, 130),
        (10, 13, False, False, 129),
        # perfect flag: highest roll for a positive base, lowest for a negative one
        (15, 19, True, False, 130),
        (-6000, -4200, True, False, 70),
        # negative base: roll range 70-130, worst value at the highest roll
        (-200, -174, False, False, 87),
        (-45, -35, False, False, 78),
        # inverted stat (spell cost) on the API's sign: range follows Artemis' positive base
        (-4, -5, False, True, 125),
        (-4, -5, True, True, 130),
        (-4, -1, False, True, 30),
    ],
)
def test_estimate_internal_roll(base, value, perfect, inverted, expected):
    assert estimate_internal_roll(base, value, perfect, inverted) == expected


def test_from_value_consumes_entry():
    # value 39 (zigzag 78), vanilla meter flag, meter offset 31, then a trailing byte
    data = [78, 4, 31, 99]
    identification = Identification.from_value("thunderDamage", 77, 31, data)
    assert identification == Identification("thunderDamage", 77, 31, 126, 39)
    assert data == [99]

    # spell cost: Artemis' +5 becomes the API's -5, perfect flag, no meter
    data = [10, 1]
    identification = Identification.from_value("raw1stSpellCost", 37, -4, data)
    assert identification == Identification("raw1stSpellCost", 37, -4, 130, -5)
    assert data == []
