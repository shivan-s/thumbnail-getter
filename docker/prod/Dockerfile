FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUNBUFFERED 1

WORKDIR /code

# install python dependences
# install pip-tools and pip
# hadolint ignore=DL3013
RUN pip install --no-cache-dir -U pip-tools pip
COPY requirements.in .

# hadolint ignore=DL3042
RUN pip-compile -o requirements.txt requirements.in && \
    pip install --no-cache-dir --no-deps -r requirements.txt

# run entry scripts
COPY ./docker/prod/entrypoint.sh .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "/code/docker/prod/entrypoint.sh"]
