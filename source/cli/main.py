"""Main entry point for the CLI application."""
import typer
from commands.balance import balance
from commands.t import t
from commands.view import view

app = typer.Typer(add_completion=False)
app.command()(t)
app.command()(balance)
app.command()(view)

if __name__ == "__main__":
    app()
