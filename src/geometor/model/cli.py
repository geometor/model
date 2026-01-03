from __future__ import annotations

from rich.console import Console

from geometor.model import Model

console = Console()


def run() -> None:
    """Run the CLI REPL."""
    model = Model("cli_model")
    console.print("[bold green]Geometor CLI[/bold green]")
    console.print("Commands:")
    console.print("  [cyan]LABEL = x, y[/cyan]   : Create a point (e.g., A = 0, 0)")
    console.print("  [cyan]* x, y[/cyan]       : Create a point with auto-generated label")
    console.print("  [cyan][ A B ][/cyan]         : Create a line connecting points A and B")
    console.print("  [cyan]( A B )[/cyan]         : Create a circle with center A and radius point B")
    console.print("  [cyan]< A B C >[/cyan]       : Create a polygon (3+ points)")
    console.print("  [cyan]/ A B /[/cyan]         : Create a segment from A to B")
    console.print("  [cyan]} A B C {[/cyan]       : Create a section (3 collinear points)")
    console.print("  [cyan]< A B C )[/cyan]       : Create a wedge (Center A, Radius/Start B, Sweep End C)")
    console.print("  [cyan]exit[/cyan] / [cyan]quit[/cyan]    : Exit the program")
    console.print()

    while True:
        try:
            command = console.input("[bold blue]>[/bold blue] ")
            if command.lower() in ("exit", "quit"):
                break
            model.parse_command(command)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
