# Тестовое приложение

# Клонируйте проект командой: `git clone https://github.com/MaksLevchenko/Messenger.git`

## Переименнуйте файл .env.dev в .env и присвойте переменным внутри него актуальные данные

### Переменные окружения

* PG_DB
* PG_PASSWORD

* secret
* algorithm

* email
* email_secret

## В терминале перейдите в папку src командой `cd /api/src`

# При запущеном docker descktop выполните команду: `docker-compose build`

# После окончания сборки контейнера выполните: `docker-compose up -d`

# Затем нужно применить миграции. Для этого выполните команду: `docker compose exec messenger alembic upgrade head`

### Теперь перейдите в браузере по адресу: `http://127.0.0.1:8000/docs#/`

### Либо можно сразу перейти на страницу регистрации: `http://127.0.0.1:8000//welcome`
