from pathlib import Path
import dotenv

from pydantic import model_validator, PostgresDsn

from pydantic_settings import BaseSettings, SettingsConfigDict


dotenv.load_dotenv()


class Settings(BaseSettings):
    # Конфигурация модели
    model_config = SettingsConfigDict(
        env_file="../.env",  # Файл с переменными окружения
        extra="ignore",  # Игнорируем лишние значения в env файле
    )

    # app = FastAPI() params
    app_root_path: str = ""
    app_openapi_url: str = ""
    app_swagger_url: str | None = "/docs"
    app_version: str = "0.0.1"

    # Postgres
    pg_scheme: str = "postgresql+psycopg"
    pg_host: str = "127.0.0.1"
    pg_port: int = 5432
    pg_db: str | None = None
    pg_user: str = "postgres"
    pg_password: str | None = None

    pg_engine_echo: bool = False  # # Вывод сгенерированных запросов в логи

    postgres_url: str | None = None

    # hash
    secret: str | None = None
    algorithm: str | None = None

    # email
    email: str | None = None
    email_secret: str | None = None

    @model_validator(mode="after")
    def setting_validator(self) -> "Settings":
        file_version = ".version"
        if Path(file_version).exists():
            with open(file_version, "r") as fp:
                self.app_version = fp.readline()

        if not self.postgres_url:
            self.postgres_url = str(
                PostgresDsn.build(
                    scheme=self.pg_scheme,
                    username=self.pg_user,
                    password=self.pg_password,
                    host=self.pg_host,
                    # host="database",
                    port=self.pg_port,
                    path=self.pg_db,
                )
            )

        return self


settings = Settings()


def get_auth_data():
    return {"secret": settings.secret, "algorithm": settings.algorithm}
