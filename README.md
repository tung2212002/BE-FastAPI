# Backend TVNow
1. Install docker follow [this](https://docs.docker.com/desktop/install/linux/).
1. Run `cp .env.example .env` to copy from `.env.example` to `.env`.
1. Create Server Gmail and update `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`.
1. Create Google OAuth 2.0 and update `GOOGLE_CLIENT_ID`, `GOOGLE_PROJECT_ID`, `GOOGLE_REDIRECT`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `GOOGLE_JAVASCRIPT_ORIGIN`.
1. Create AWS S3 and update `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `AWS_BUCKET_NAME`.
1. Run `docker compose up -d`.
1. Run `docker ps -a` to list running containers
1. Run `docker exec -it tvnow-api sh` to access docker container api shell.
    - In container shell, run `alembic revision --autogenerate -m "Initial migration"`.
    - In container shell, run `alembic upgrade head`.


