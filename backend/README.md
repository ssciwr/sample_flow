# SampleFlow Backend

The Flask REST API backend for SampleFlow.

Note: these are development install/use instructions, see
[README_DEV.md](https://github.com/ssciwr/sample_flow/blob/main/README_DEV.md)
for instructions on running the full production docker-compose setup locally.

## Installation

```pycon
pip install -e .[tests]
```

## Use

To start a local development server for testing purposes:

```bash
sample_flow_server
```

Type `sample_flow_server --help` to see the command line options:

```bash
Usage: sample_flow_server [OPTIONS]

Options:
  --host TEXT       [default: localhost]
  --port INTEGER    [default: 8080]
  --data-path TEXT  [default: .]
  --help            Show this message and exit.
```

## Tests

```pycon
pytest
```

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
