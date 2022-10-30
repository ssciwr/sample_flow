# CircuitSEQ website prototype
[![CI](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssciwr/circuit_seq/branch/main/graph/badge.svg?token=Z8fyKbjrHd)](https://codecov.io/gh/ssciwr/circuit_seq)

A work-in-progress prototype of the CircuitSEQ website.

## Docker

To run the website locally in docker containers (on linux, with docker-compose installed):

```sh
git clone https://github.com/ssciwr/circuit_seq.git
cd circuit_seq
docker-compose up --build
```

The website is then served at http://localhost:8080/

Built-in accounts for testing:

- admin account
	- email: admin@embl.de
	- password: admin
- user account
	- email: user@embl.de
	- password: user

## Backend

The backend is a Python Flask REST API, see [backend/README.md](backend/README.md) for more details.

## Frontend

The frontend is a vue.js app, see [frontend/README.md](frontend/README.md) for more details.
