"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-08 15:30:39
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-08 15:56:11
FilePath     : /tests/test_item.py
"""

from wynntilsresolver.blocks import End, GearItem, Identification, Identifications, Name, Powder, Reroll, Shiny, Version
from wynntilsresolver.item import GearItemResolver


def test_decoding_item():
    # shiny_warp = "󰀀󰄀󰉗󶅲󷀀󰌉󰀘󵜢󴵅󶈑󴝑󷐙󵀄󶸥󵠦󶠄󰌃󿞼󰘄󸨁􏿮"
    shiny_warp_v1 = "󰀀󰄀󰉗󶅲󷀀󰌉󰄁󲤲󴖴󰄰󱅤󴔢󵥍󱢏󰍊󱦯󰥢󱜻󵰄󱸲󵇨󰉧󲛖󰑒󰐃󰀆󰜀􏿮"
    shiny_warp_v2 = "󰀁󰄀󰉗󶅲󷀀󰌉󰄁󲤲󴖴󰅚󱅤󷼢󵥔󱢏󰍕󱦯󰥌󱜻󵘄󱹀󵇨󰉧󲛖󰑱󰐃󰏷󻰅󰈆󰄁󰃿"

    # sw = GearItemResolver.from_utf16(shiny_warp)
    sw1 = GearItemResolver.from_utf16(shiny_warp_v1)
    sw2 = GearItemResolver.from_utf16(shiny_warp_v2)

    assert GearItemResolver._attrs == {
        "start": Version,
        "item_type": GearItem,
        "_name": Name,
        "_identifications": Identifications,
        "powder": Powder,
        "shiny": Shiny,
        "_reroll": Reroll,
        "end": End,
    }

    # Test shiny warp v1
    assert sw1.name == "Warp"
    assert sw1.identifications
    assert sw1.identifications == [
        Identification(id="rawAgility", internal_id=41, base=25, roll=-1, value=25),
        Identification(id="reflection", internal_id=69, base=90, roll=48, value=43),
        Identification(id="exploding", internal_id=17, base=50, roll=69, value=35),
        Identification(id="manaRegen", internal_id=34, base=-45, roll=77, value=-35),
        Identification(id="healthRegen", internal_id=24, base=-200, roll=74, value=-148),
        Identification(id="healthRegenRaw", internal_id=25, base=-600, roll=98, value=-588),
        Identification(id="healingEfficiency", internal_id=23, base=-30, roll=92, value=-28),
        Identification(id="airDamage", internal_id=4, base=15, roll=50, value=8),
        Identification(id="walkSpeed", internal_id=81, base=180, roll=103, value=185),
        Identification(id="raw2ndSpellCost", internal_id=38, base=299, roll=82, value=245),
    ]
    assert sw1.powder
    assert sw1.powder.powder_slots == 3
    assert sw1.powder.powders == []
    assert sw1.shiny
    assert sw1.shiny.name == "deaths"
    assert sw1.shiny.value == 0
    assert sw1.shiny.display_name == "Deaths"
    assert sw1.shiny.internal_id == 7
    assert sw1.reroll == 0

    # Test shiny warp v2
    assert sw2.name == "Warp"
    assert sw2.identifications
    assert sw2.identifications == [
        Identification(id="rawAgility", internal_id=41, base=25, roll=-1, value=25),
        Identification(id="reflection", internal_id=69, base=90, roll=90, value=81),
        Identification(id="exploding", internal_id=17, base=50, roll=127, value=64),
        Identification(id="manaRegen", internal_id=34, base=-45, roll=84, value=-38),
        Identification(id="healthRegen", internal_id=24, base=-200, roll=85, value=-170),
        Identification(id="healthRegenRaw", internal_id=25, base=-600, roll=76, value=-456),
        Identification(id="healingEfficiency", internal_id=23, base=-30, roll=86, value=-26),
        Identification(id="airDamage", internal_id=4, base=15, roll=64, value=10),
        Identification(id="walkSpeed", internal_id=81, base=180, roll=103, value=185),
        Identification(id="raw2ndSpellCost", internal_id=38, base=299, roll=113, value=338),
    ]
    assert sw2.powder
    assert sw2.powder.powder_slots == 3
    assert sw2.powder.powders == ["A6", "A6", "A6"]
    assert sw2.shiny
    assert sw2.shiny.name == "mobsKilled"
    assert sw2.shiny.value == 0
    assert sw2.shiny.display_name == "Mobs Killed"
    assert sw2.shiny.internal_id == 1
    assert sw2.reroll == 2


def test_decoding_item_v3():
    # V3: identifications carry the value, flags and vanilla meter instead of the internal roll
    cataclysm_v3 = "󰀂󰄀󰉍󶅳󷑥󷉷󶽲󶬠󴍡󷑡󶍬󷥳󶴀󰌆󰁋󰰄󱩌󳐄󰬸󼽁󰔣󴵎󰐟󲔊󰐣󲜊󰐣󰐃󰀅󰋿"

    item = GearItemResolver.from_utf16(cataclysm_v3)

    assert item.name == "Masterwork Cataclysm"
    assert item.identifications == [
        Identification(id="rawDexterity", internal_id=47, base=30, roll=-1, value=30),
        Identification(id="stealing", internal_id=75, base=5, roll=120, value=6),
        Identification(id="thorns", internal_id=76, base=40, roll=65, value=26),
        # perfect flag set: roll is the perfect roll of a negative base
        Identification(id="rawHealth", internal_id=56, base=-6000, roll=70, value=-4200),
        Identification(id="thunderDamage", internal_id=77, base=31, roll=126, value=39),
        # spell costs are encoded on Artemis' inverted sign, normalized back to the API's
        Identification(id="raw1stSpellCost", internal_id=37, base=-4, roll=125, value=-5),
        Identification(id="raw3rdSpellCost", internal_id=39, base=-4, roll=125, value=-5),
    ]
    assert item.powder
    assert item.powder.powder_slots == 3
    assert item.powder.powders == []
    assert item.shiny is None
    assert item.reroll == 2
