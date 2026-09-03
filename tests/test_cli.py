import json

from typer.testing import CliRunner
from wynntilsresolver.cli import app

runner = CliRunner()

CATACLYSM_V3 = "󰀂󰄀󰉍󶅳󷑥󷉷󶽲󶬠󴍡󷑡󶍬󷥳󶴀󰌆󰁋󰰄󱩌󳐄󰬸󼽁󰔣󴵎󰐟󲔊󰐣󲜊󰐣󰐃󰀅󰋿"


def test_decode_pretty():
    result = runner.invoke(app, [CATACLYSM_V3])
    assert result.exit_code == 0
    assert "Masterwork Cataclysm" in result.output
    assert "raw1stSpellCost" in result.output
    assert "fixed" in result.output  # pre-identified rawDexterity


def test_decode_json_from_stdin():
    result = runner.invoke(app, ["--json"], input=CATACLYSM_V3)
    assert result.exit_code == 0
    item = json.loads(result.output)
    assert item["name"] == "Masterwork Cataclysm"
    assert item["version"] == 2
    assert item["reroll"] == 2
    assert item["shiny"] is None
    assert item["powder"] == {"slots": 3, "powders": []}
    assert item["identifications"][1] == {"id": "stealing", "internal_id": 75, "base": 5, "roll": 120, "value": 6}


def test_decode_reports_parse_failure():
    result = runner.invoke(app, ["󰀃󰄀"])
    assert result.exit_code == 1
    assert "Unsupported encoding version 3" in result.output


def test_decode_rejects_empty_input():
    result = runner.invoke(app, ["-"], input="  \n")
    assert result.exit_code == 2
