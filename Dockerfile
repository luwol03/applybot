FROM python:3.8-alpine AS builder

RUN apk add --no-cache gcc~=10.2 musl-dev~=1.2 git~=2.30

WORKDIR /build

RUN pip install pipenv==2020.11.15

COPY Pipfile /build/
COPY Pipfile.lock /build/

ARG PIPENV_NOSPIN=true
ARG PIPENV_VENV_IN_PROJECT=true
RUN pipenv install --deploy --ignore-pipfile

COPY .git /build/.git/
RUN git describe --tags > VERSION

FROM python:3.8-alpine

RUN set -x \
    && apk add --no-cache bash~=5.1 \
    && addgroup -g 1000 bot \
    && adduser -G bot -u 1000 -s /bin/bash -D -H bot

WORKDIR /app

USER bot

COPY --from=builder /build/.venv/lib /usr/local/lib
COPY --from=builder /build/VERSION /app/

COPY . /app/

CMD python applybot.py
