FROM python:3.7-alpine

ENV LISTEN_HOST "0.0.0.0"
ENV LISTEN_PORT "8000"
ENV POSTGRES_HOST "jassets-postgres"
ENV POSTGRES_PORT "5432"
ENV POSTGRES_USER "jassets"
ENV POSTGRES_PASSWORD ""
ENV LOG_LEVEL "INFO"
ENV SENTRY_DSN ""
ENV STATIC_URL "https://jassets-storage.s3-eu-west-1.amazonaws.com/"
ENV STATIC_RELOAD_INTERVAL "60"
ENV DOCKERIZE_VERSION "v0.6.1"

RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN addgroup -g 111 app \
 && adduser -D -u 111 -G app app \
 && mkdir -p /app \
 && chown -R app:app /app \
 && mkdir -p /src \
 && chown -R app:app /src

RUN apk update

# build dependencies
RUN apk add gcc musl-dev postgresql-dev git

WORKDIR /app

COPY --chown=app:app requirements.txt /app/
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir --src /src/ -r requirements.txt

RUN chown -R app:app /src/

COPY --chown=app:app . /app

USER app

ENTRYPOINT ["/app/run.sh"]
