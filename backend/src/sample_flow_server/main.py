from __future__ import annotations
import click
from sample_flow_server import create_app


@click.command()
@click.option("--host", default="localhost", show_default=True)
@click.option("--port", default=8080, show_default=True)
@click.option("--data-path", default=".", show_default=True)
def main(host: str, port: int, data_path: str):
    app = create_app(data_path=data_path)
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
