from __future__ import annotations
import click
from circuit_seq_server import create_app


@click.command()
@click.option("--host", default="localhost", show_default=True)
@click.option("--port", default=8080, show_default=True)
@click.option("--data-path", default=".", show_default=True)
@click.option("--ssl-cert", default="./cert.pem", show_default=True)
@click.option("--ssl-key", default="./key.pem", show_default=True)
def main(host: str, port: int, data_path: str, ssl_cert: str, ssl_key: str):
    app = create_app(data_path=data_path)
    app.run(host=host, port=port, ssl_context=(ssl_cert, ssl_key))


if __name__ == "__main__":
    main()
