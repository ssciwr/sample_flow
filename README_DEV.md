# CircuitSEQ website prototype

Some information on how to locally build and deploy the website if you would like to make changes to the code.

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

### Docker

Both the backend and the frontend have a Dockerfile, and there is docker-compose file to coordinate them.
