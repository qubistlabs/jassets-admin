# jassets-admin
Django-based UI for jassets management

## Getting started

`docker-compose -f docker-compose.yml up -d jassets-admin`

UI will be available at `localhost:8001` by default

## Configuration
Available environment variables:

- `SECRET_KEY` - django setting for making hashes
- `POSTGRES_HOST` (default `0.0.0.0`) - DB server host address
- `POSTGRES_PORT` (default `9543`) - DB server port
- `POSTGRES_USER` (default `jassets`) - DB server user name
- `POSTGRES_PASSWORD` (default is empty) - DB server password
- `POSTGRES_DB` (default `jassets`) - DB name
- `ADMIN_LOGIN` (default `admin`) - super user name
- `ADMIN_PASSWORD` (default `admin`) - super user password
- `ADMIN_EMAIL` (default is empty) - super user email address
