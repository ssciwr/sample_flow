# CircuitSeq Backend

The Flask REST API backend for [circuitseq.iwr.uni-heidelberg.de](https://circuitseq.iwr.uni-heidelberg.de/).

Note: these are development install/use instructions, see
[README_DEV.md](https://github.com/ssciwr/circuit_seq/blob/main/README_DEV.md)
for instructions on running the full production docker-compose setup locally.

## Installation

```pycon
pip install -e .[tests]
```

## Use

To start a local development server for testing purposes:

```bash
circuit_seq_server
```

Type `circuit_seq_server --help` to see the command line options:

```bash
Usage: circuit_seq_server [OPTIONS]

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
