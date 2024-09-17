# syntax=docker/dockerfile:1
FROM python:3.12 as base


WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN --mount=type=ssh pip install .

FROM base as prod
CMD [ "python", "-m", "users_ms"]