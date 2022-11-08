from __future__ import annotations
import click
from circuit_seq_server import create_app


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=5000, show_default=True)
def main(host: str, port: int):
    app = create_app()
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
