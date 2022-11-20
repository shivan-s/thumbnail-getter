# Thumbnail Getter

Download thumbnails for videos of a particular YouTube channel.

## Requires

- Docker
- Docker compose
- Makefile

## Instructions

0. (Make instructions better.)

1. [Login into the google console](https://console.cloud.google.com/) and create credentials. API should be fine.
   [auth]!(./docs/authentication.png)

2. Enable YouTube Data API v3 via the console.
   [enable]!(./docs/enable-api.png)

3. Set up `.env` file (have a look at `.env.example`):

```shell
# .env
YT_APP_KEY=<PUT API KEY HERE>
```

4. Run programme:

```shell
make run
```

## Contributing

Be nice. Also, ensure you have the above requirements (plus `pre-commit`)

Install pre-commit

```
pre-commit install
```
