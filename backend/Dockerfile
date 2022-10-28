FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install .

CMD ["circuit_seq_server", "--host", "0.0.0.0", "--port", "5000"]
