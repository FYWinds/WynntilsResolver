"""Command line front-end. Needs the optional `cli` extra: `pip install "wynntilsresolver[cli]"`."""

import dataclasses
import json
import sys
from typing import Any, Dict, Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from .exception import ResolverException
from .item import GearItemResolver

app = typer.Typer(add_completion=False)
stdout = Console()
stderr = Console(stderr=True, soft_wrap=True)


def _read_data(data: Optional[str]) -> str:
    if data is None and sys.stdin.isatty():
        # Nothing was piped in: waiting on the terminal would look like a hang.
        raise typer.BadParameter("pass the encoded item as DATA or pipe it to stdin", param_hint="DATA")
    text = (sys.stdin.read() if data is None or data == "-" else data).strip()
    if not text:
        raise typer.BadParameter("no input data", param_hint="DATA")
    return text


def _to_dict(item: GearItemResolver) -> Dict[str, Any]:
    return {
        "name": item.name,
        "version": item.start.version,
        "reroll": item.reroll,
        "identifications": [dataclasses.asdict(i) for i in item.identifications or []],
        "powder": {"slots": item.powder.powder_slots, "powders": item.powder.powders} if item.powder else None,
        "shiny": {
            "name": item.shiny.name,
            "internal_id": item.shiny.internal_id,
            "display_name": item.shiny.display_name,
            "value": item.shiny.value,
            "reroll": item.shiny.reroll,
        }
        if item.shiny
        else None,
    }


def _print_item(item: GearItemResolver) -> None:
    # Artemis names the version bytes 0, 1, 2 as VERSION_1..3
    stdout.print(f"[bold]{item.name}[/] [dim]encoding V{item.start.version + 1}, rerolls {item.reroll}[/]")

    if item.powder:
        powders = " ".join(item.powder.powders) or "none"
        stdout.print(f"Powders  {powders} [dim]({len(item.powder.powders)}/{item.powder.powder_slots})[/]")
    if item.shiny:
        stdout.print(f"Shiny    {item.shiny.display_name}: {item.shiny.value} [dim](rerolls {item.shiny.reroll})[/]")

    if item.identifications:
        table = Table(box=box.SIMPLE_HEAD, pad_edge=False)
        table.add_column("Identification")
        table.add_column("Base", justify="right")
        table.add_column("Roll", justify="right")
        table.add_column("Value", justify="right")
        for i in item.identifications:
            roll = "[dim]fixed[/]" if i.roll < 0 else f"{i.roll}%"
            table.add_row(i.id, str(i.base), roll, str(i.value))
        stdout.print(table)


@app.command()
def decode(
    data: Annotated[
        Optional[str],
        typer.Argument(help="UTF-16 encoded item string. Use '-' or omit to read from stdin.", show_default=False),
    ] = None,
    drop_unknown: Annotated[
        bool, typer.Option("--drop-unknown", help="Skip unknown bytes instead of failing.")
    ] = False,
    as_json: Annotated[bool, typer.Option("--json", help="Print the decoded item as JSON.")] = False,
) -> None:
    """Decode a Wynntils (Artemis) chat-encoded gear item."""
    try:
        item = GearItemResolver.from_utf16(_read_data(data), drop_unknown=drop_unknown)
    except ResolverException as e:
        # ParseFailed wraps the block-level error, which carries the actual reason
        reason = f"{e}: {e.__cause__}" if e.__cause__ else str(e)
        stderr.print(f"[red]error:[/] {reason}")
        raise typer.Exit(code=1)

    if as_json:
        typer.echo(json.dumps(_to_dict(item), ensure_ascii=False))
    else:
        _print_item(item)
