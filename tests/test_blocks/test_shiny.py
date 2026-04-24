def test_shiny_decoding():
    from wynntilsresolver.blocks import Shiny, Version

    shiny = Shiny.from_bytes([6, 7, 0], parsed_blocks=[Version(0)])
    assert shiny.name == "deaths"
    assert shiny.internal_id == 7
    assert shiny.display_name == "Deaths"
    assert shiny.value == 0

    shiny = Shiny.from_bytes([6, 7, 2, 0], parsed_blocks=[Version(1)])
    assert shiny.name == "deaths"
    assert shiny.internal_id == 7
    assert shiny.display_name == "Deaths"
    assert shiny.value == 0
    assert shiny.reroll == 2
