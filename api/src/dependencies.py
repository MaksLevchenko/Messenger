import random
import smtplib

from typing import Annotated, AsyncGenerator
from fastapi import Depends, Query, Header, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import datetime, timezone

from config.settings import get_auth_data
from db import pg_async_session
from config.settings import settings


async def add_id_to_header(id: Annotated[int, Header(alias="x-id-del")]) -> int:
    """Функция добавляет id в header"""

    return id


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """в модуле
    from sqlalchemy.ext.asyncio import AsyncSession

    def _get(db: Annotated[AsyncSession, Depends(get_session)]):
        ...
    """
    async with pg_async_session() as _session:
        yield _session


class Pagination:
    def __init__(
        self, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, max=1000)
    ):
        self.offset = offset
        self.limit = limit

    @property
    def dict(self):
        return {"offset": self.offset, "limit": self.limit}


def get_token(request: Request):
    """Получает jwt из cookie"""
    token = request.cookies.get("access_token")
    if token:
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не обнаружен"
        )


async def get_auth_user(token: str = Depends(get_token)):
    """Получает авторизованного пользователя и возвращает его id"""
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            token, auth_data["secret"], algorithms=[auth_data["algorithm"]]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден"
        )

    expire = payload.get("exp")

    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не найден id пользователя"
        )
    return user_id


def send_email(address: str, text: str) -> bool:
    """Отправляет сообщение на нужный email"""

    # Настраиваем почту для отправки сообщений
    server = "smtp." + settings.email.split("@")[1]
    smtp_server = smtplib.SMTP(server, 587)
    smtp_server.starttls()
    smtp_server.login(settings.email, settings.email_secret)

    # Отправляем сообщение
    send = smtp_server.sendmail(settings.email, address, text)
    if not send:
        return True


def get_random() -> int:
    """Генерирует случайное 4х значное число"""
    mylist = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    x1 = int(random.choice(mylist))
    x2 = int(random.choice(mylist))
    x3 = int(random.choice(mylist))
    x4 = int(random.choice(mylist))
    x = x1 * 1000 + x2 * 100 + x3 * 10 + x4
    return x
