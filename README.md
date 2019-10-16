# jassets-admin
Django-based UI for jassets management

## Getting started

`docker-compose -f docker-compose.yml up -d jassets-admin`

UI will be available at `localhost:8001` by default

## Configuration
Available environment variables (all of them are required, especially if there is no default value) :

- `SECRET_KEY` - django setting for making hashes
- `ALLOWED_HOSTS` (default is `["*"]`) - list of allowed hosts. must be a json parsable string
- `DEBUG` (default `0` what equals `False`) - django debug mode

- `POSTGRES_HOST` (default `0.0.0.0`) - DB server host address
- `POSTGRES_PORT` (default `5432`) - DB server port
- `POSTGRES_USER` (default `postgres`) - DB server user name
- `POSTGRES_PASSWORD` (default is empty) - DB server password
- `POSTGRES_DB` (default `jassets`) - DB name

- `ADMIN_LOGIN` (default `admin`) - super user name
- `ADMIN_PASSWORD` (required) - super user password
- `ADMIN_EMAIL` (default is empty) - super user email address

- `LISTEN_HOST` - hostname to start server by runserver command
- `LISTEN_PORT` (default `8080`) port to start server by runserver command

- `VALIDATOR_HOST` (default is empty) - host of asset validation service
- `VALIDATOR_PORT` (default is empty) - port of asset validation service
- `VALIDATION_TIMEOUT` (default `1`) - interval in seconds between checks for asset validation results
