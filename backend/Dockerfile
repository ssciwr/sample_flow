FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/ssciwr/sample_flow
LABEL org.opencontainers.image.description="SampleFlow backend production image"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY . .

RUN pip install .

CMD ["gunicorn", "--bind", "backend:8080", "sample_flow_server:create_app()"]
