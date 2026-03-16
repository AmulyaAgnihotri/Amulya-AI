# ============================================================
#  ui.py  —  Elegant Terminal Interface
# ============================================================
import sys
sys.stdout.reconfigure(encoding="utf-8")  # pyre-ignore[16]

from rich.console import Console   # pyre-ignore[21]
from rich.panel import Panel       # pyre-ignore[21]
from rich.text import Text         # pyre-ignore[21]
from rich import box               # pyre-ignore[21]
from config import ASSISTANT_NAME  # pyre-ignore[21]

con = Console(highlight=False)


def banner():
    con.print()
    con.print(f"  [bold cyan]━━━  {ASSISTANT_NAME}  ━━━[/bold cyan]")
    con.print(f"  [dim]Voice assistant  ·  System online[/dim]")
    con.print()


def status(msg, style="dim"):
    con.print(f"  [{style}]› {msg}[/{style}]")


def user(text):
    con.print()
    con.print(Panel(
        Text(text, style="bold white"),
        title="[green]You[/green]",
        title_align="left",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 2),
    ))


def ai(text):
    con.print(Panel(
        Text(text, style="white"),
        title=f"[cyan]{ASSISTANT_NAME}[/cyan]",
        title_align="right",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 2),
    ))
    con.print()


def error(msg):
    con.print(f"  [bold red]error: {msg}[/bold red]")
