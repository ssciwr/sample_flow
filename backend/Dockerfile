FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "circuit_seq_server:create_app()"]
