FROM python:3.10-slim

LABEL org.opencontainers.image.source=https://github.com/ssciwr/circuit_seq
LABEL org.opencontainers.image.description="CircuitSEQ backend production image"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY . .

RUN pip install .

CMD ["gunicorn", "--certfile", "/circuit_seq_ssl_cert.pem", "--keyfile", "/circuit_seq_ssl_key.pem", "--bind", "0.0.0.0:8080", "circuit_seq_server:create_app()"]
