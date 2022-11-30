# CircuitSEQ website developer info

Some information on how to locally build and deploy the website if you would like to make changes to the code.

## Run locally with docker-compose

To run the website locally in docker containers on your computer (on linux, with docker-compose installed):

```sh
git clone https://github.com/ssciwr/circuit_seq.git
cd circuit_seq
docker-compose up --build
```

### Database

The database will by default be stored in a `docker_volume` folder
in the folder where you run the docker-compose command.
To modify this location, set the `CIRCUIT_SEQ_DATA` environment variable.

### SSL

SSL cert/key by default are assumed to exist as `cert.pem` and `key.pem`
in the folder where you run the docker-compose command.
To point to different files, set the `CIRCUIT_SEQ_SSL_CERT` and `CIRCUIT_SEQ_SSL_KEY` environment variables.

To generate a cert/key pair:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj '/CN=localhost'
```

### Secret Key

JWT tokens used for authentication are generated using a secret key.
This can be set using the `CIRCUIT_SEQ_JWT_SECRET_KEY` environment variable.
If this is not set or is less than 16 chars, a new random secret key is generated when the server starts.

### URL

The website is then served at https://localhost/
Note that the SSK keys are self-signed keys and your browser will still warn about the site being insecure.

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
cd ..
circuit_seq_server
```

Install and run the frontend:

```sh
cd frontend
npm install
npm run dev
```

The website is then served at http://localhost:5173/

## Implementation

### Backend

The backend is a Python Flask REST API, see [backend/README.md](backend/README.md) for more details.

### Frontend

The frontend is a vue.js app, see [frontend/README.md](frontend/README.md) for more details.

### Docker

Both the backend and the frontend have a Dockerfile, and there is docker-compose file to coordinate them.

## Production deployment

Same as docker-compose but with additional `.env` and `frontend/.env.local` files
to set location of database, cert/key pair from letsencrypt, and public url.

### To deploy

```
cd circuit_seq
# check current status
sudo docker-compose ps
# see current logs
sudo docker-compose logs
# update code
git fetch && git pull
# re-build & re-launch containers
sudo docker-compose up --build -d
```

### Make admin users

To make an existing user with email `user@embl.de` into an admin, ssh into the VM, then

```
cd circuit_seq
sudo sqlite3 docker_volume/CircuitSeq.db
sqlite> UPDATE user SET is_admin=true WHERE email='user@embl.de';
sqlite> .quit
```
