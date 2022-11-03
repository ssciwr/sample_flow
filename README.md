# CircuitSEQ website prototype
[![CI](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssciwr/circuit_seq/branch/main/graph/badge.svg?token=Z8fyKbjrHd)](https://codecov.io/gh/ssciwr/circuit_seq)

A work-in-progress prototype of the CircuitSEQ website.

## Try it out online

It is now running on a heiCLOUD VM here: http://129.206.7.129/

### Testing accounts

There are currently two built-in accounts for testing purposes:

- admin account
	- email: `admin@embl.de`
	- password: `admin`
- user account
	- email: `user@embl.de`
	- password: `user`

You can also signup for a new account on the site (there is not yet an email account activation step, you can login straightaway after signup)

### Implemented features

- Users can
  - sign up with a valid email address
  - request a sample, optionally providing a fasta reference sequence
  - see a list of their requested samples & download the reference sequences
- Admins can
  - see a list of all requested samples & download reference sequences
  - see a list of all users

### Notes

- all uploaded samples and registered users will be deleted without warning as the prototype is updated!

## Run locally with docker-compose

To run the website locally in docker containers on your computer (on linux, with docker-compose installed):

```sh
git clone https://github.com/ssciwr/circuit_seq.git
cd circuit_seq
docker-compose up --build
```

The website is then served at http://localhost:8080/

## Run locally with Python and npm

Clone the repo:
```sh
git clone https://github.com/ssciwr/circuit_seq.git
cd circuit_seq
```
Install and run the backend:
```sh
cd backend
pip install .
circuit_seq_server
```
Install and run the frontend:
```sh
cd frontend
npm install
npm run dev -- --host=8080
```

The website is then served at http://localhost:8080/

## Implementation

### Backend

The backend is a Python Flask REST API, see [backend/README.md](backend/README.md) for more details.

### Frontend

The frontend is a vue.js app, see [frontend/README.md](frontend/README.md) for more details.
