# jassets-admin
Django-based UI for jassets management

Launch script (run.sh) may be invoked in 4 modes depending of `RUNMODE` env var:
- `app` option is to run main application server
- `validation_daemon` constantly checks validation results from jassets-validator service. No need to wait for its completion
- `clear_validation_queue` clears all tasks for validation
- `test` executes pytest 

Normally app must be launched in two processes - in `app` and in `validation_daemon` mode

## Getting started

`docker-compose -f docker-compose.yml up -d jassets-admin`

UI will be available at `localhost:8001` by default

## Configuration
Available environment variables (all of them are required, especially if there is no default value) :

#### launch config
- `RUNMODE` (default `app`) - what to launch. Possible values: `test`, `validation_daemon`, `clear_validation_queue`, `app`

#### Django config

- `SECRET_KEY` - django setting for making hashes
- `ALLOWED_HOSTS` (default is `["*"]`) - list of allowed hosts. must be a json parsable string
- `DEBUG` (default `0` what equals `False`) - django debug mode
- `MEDIA_ROOT` (default `./media`) - folder to store user files
- `DJANGO_SETTINGS_MODULE` (default `jassets_admin.settings`) - django settings module


- `LISTEN_HOST` - hostname to start server by runserver command
- `LISTEN_PORT` (default `8080`) port to start server by runserver command


- `ADMIN_LOGIN` (default `admin`) - super user name
- `ADMIN_PASSWORD` (required) - super user password
- `ADMIN_EMAIL` (default is empty) - super user email address

#### jassets DB config

- `POSTGRES_HOST` (default `jassets-postgres`) - DB server host address
- `POSTGRES_PORT` (default `5432`) - DB server port
- `POSTGRES_USER` (default `postgres`) - DB server user name
- `POSTGRES_PASSWORD` (default is empty) - DB server password
- `POSTGRES_DB` (default `jassets`) - DB name

#### jassets-validator connection config

- `VALIDATOR_HOST` (default is empty) - host of asset validation service (jassets-validator)
- `VALIDATOR_PORT` (default is empty) - port of asset validation service (jassets-validator)
- `VALIDATION_TIMEOUT` (default `1`) - interval in seconds between checks for asset validation results

#### config for accessing asset files stored in S3

- `AWS_ACCESS_KEY` - Amazon S3 storage access key
- `AWS_SECRET_ACCESS_KEY` - Amazon S3 storage secret access key 
- `AWS_SECRET_TOKEN` - Amazon S3 storage secret token
- `AWS_BUCKET_NAME` (default `jassets-storage`) - Amazon S3 storage bucket name
