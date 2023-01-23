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

### User signup activation email

When you sign up for an account when running locally it will send an email (if port 25 is open) to whatever address you use.
If the port is blocked you can see the activation_token in the docker logs, and activate your local account by going to https://localhost/activate/activation_token_from_logs
To make yourself an admin user, see the production deployment section below.

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

Same as docker-compose but instead of building from source there are also public production containers
built by CI that can be pulled, so all that is needed to deploy the latest version is to download the docker-compose.yml file, then

```
sudo docker-compose pull
sudo docker-compose up -d
```

The location of data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker-compose.yml, e.g.:

```
CIRCUIT_SEQ_DATA="/home/ubuntu/circuit_seq/docker_volume"
CIRCUIT_SEQ_SSL_CERT="/etc/letsencrypt/live/circuitseq.iwr.uni-heidelberg.de/fullchain.pem"
CIRCUIT_SEQ_SSL_KEY="/etc/letsencrypt/live/circuitseq.iwr.uni-heidelberg.de/privkey.pem"
CIRCUIT_SEQ_JWT_SECRET_KEY="abc123" # to generate a new secret key: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
```

The current status of the containers can be checked with

```
sudo docker-compose ps
sudo docker-compose logs
```

### Renew SSL certificate

Certbot attempts to auto-renew but this requires port 80, which is already taken by our web server.
To update the certificate manually:

```
sudo docker-compose down
sudo certbot renew
sudo docker-compose up -d
```

### Give users admin rights

To make an existing user with email `user@embl.de` into an admin, ssh into the VM, then

```
cd circuit_seq
sudo sqlite3 docker_volume/CircuitSeq.db
sqlite> UPDATE user SET is_admin=true WHERE email='user@embl.de';
sqlite> .quit
```
