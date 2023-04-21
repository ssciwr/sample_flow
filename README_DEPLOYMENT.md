# CircuitSEQ website deployment info

Some information on how to deploy the website - currently it is deployed on a heicloud VM.

## Production deployment

Production docker container images are automatically built by CI.
To deploy the latest version on a virtual machine with docker-compose installed,
download [https://raw.githubusercontent.com/ssciwr/circuit_seq/main/docker-compose.yml](docker-compose.yml), then do

```
sudo docker-compose pull
sudo docker-compose up -d
```

The location of data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker-compose.yml.

For example the current deployment on heicloud looks like this:

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
