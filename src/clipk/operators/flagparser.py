""" flag parser script"""

import typer


from .clipfile_link import reset, see_saved, return_to_clipboard
from .tui import run_tui, _row_to_clip

from clipk.__about__ import __version__


app = typer.Typer(
    name="kclip",
    help="CLI clipboard manager ",
    add_completion=True,
    no_args_is_help=False,
    rich_markup_mode="markdown",
    context_settings={"help_option_names": ["-h", "--help"]}
)

def _version_callback(value: bool):
    if value:
        typer.echo(f"kclip {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="kclip",
    help="CLI clipboard manager with an interactive TUI.",
    add_completion=True,
    no_args_is_help=False,
    rich_markup_mode="markdown",
    context_settings={"help_option_names": ["-h", "--help"]},
)

def _return_nth_to_clipboard(n: int) -> None:
    """Restore the Nth saved clip (1 = oldest) to the system clipboard."""
    records = see_saved() or []
    if not records:
        typer.echo("No clips saved.")
        raise typer.Exit(code=1)

    if n < 1 or n > len(records):
        typer.echo(f"Only {len(records)} clip(s) saved; can't pick #{n}.")
        raise typer.Exit(code=1)

    row = records[n - 1]
    clip = _row_to_clip(row)

    if not return_to_clipboard(clip):
        typer.echo(
            f"Could not restore clip #{n} ({clip.clip_type}). "
            "Is xclip installed?"
        )
        raise typer.Exit(code=1)

    typer.echo(f"Restored clip #{n} ({clip.clip_type}) to clipboard.")




@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v",
        callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
    mouse: bool = typer.Option(
        False, "--mouse", "-m",
        help="Enable mouse support (not implemented yet).",
    ),
    do_reset: bool = typer.Option(
        False, "--reset", "-r",
        help="Delete all clips, files, and the database.",
    ),
    do_return: int = typer.Option(
        0, "--return", "-n",
        min=0, max=10,
        help="Restore the Nth saved clip (1=oldest, 10=newest) to the "
             "clipboard. 0 means 'not requested'.",
    ),
):
    """kclip — launch the TUI, or use one of the flags below."""
    # -v
    if version:
        return

    # -m
    if mouse:
        typer.echo("Mouse support is not implemented yet.")
        raise typer.Exit()

    # -r
    if do_reset:
        if typer.confirm("Delete EVERYTHING (clips, files, database)?"):
            reset()
            typer.echo("Reset complete.")
        else:
            typer.echo("Cancelled.")
        raise typer.Exit()

    # -n N
    if do_return:
        _return_nth_to_clipboard(do_return)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        run_tui()


@app.command()
def tui():
    """Launch the interactive TUI."""
    run_tui()


@app.command("list")
def list_clips():
    """Print all saved clips."""
    records = see_saved() or []
    if not records:
        typer.echo("No clips saved.")
        return

    typer.echo(f"{'ID':>4}  {'TYPE':<6}  {'PIN':<3}  NAME")
    typer.echo("-" * 40)
    for r in records:
        pin = "*" if r.get("isPinned") else " "
        typer.echo(
            f"{r.get('clipID', 0):>4}  "
            f"{r.get('clipType', '?'):<6}  "
            f"{pin:<3}  "
            f"{r.get('uniqueName', '?')}"
        )