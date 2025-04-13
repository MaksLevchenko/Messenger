from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession


from .auth import create_access_token, get_password_hash, verify_password
from crud.crud import add_model, get_model
from db.models import User
from dependencies import get_random, get_session, send_email
from .querys import get_user_by_email
from .schemas import UserSchema


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/welcome", response_class=HTMLResponse)
async def home_page(request: Request):
    """Выводит страницу с регистрацией или входом"""

    return templates.TemplateResponse("welcome.html", {"request": request})


@router.post("/sign-up")
async def sign_up(
    db: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    name: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
):
    """Проверяет введённые данные пользователя, и если всё хорошо, регистрирует пользователя"""

    # Пробуем получить пользователя с такими данными
    q = get_user_by_email(email=login)
    user = await get_model(db=db, q=q)

    # Если пользователь с таким email-ом существует выдаём соответствующую ошибку
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с такими данными уже существует!",
        )

    # Если пользователя с таким email-ом нет в базе, регистрируем пользователя
    else:
        password = get_password_hash(password=password)
        secret = get_random()
        send_email(
            address=login,
            text=f"Ваш секретный код с ресурса MaksiGram {secret}.\
                    Проигнорируйте это письмо, если не регистрировались на MaksiGram.\
                    Никому не сообщайте секретных кодов!".encode(
                "utf8"
            ),
        )
        secret = get_password_hash(password=str(secret))
        return templates.TemplateResponse(
            "confirmation_of_registration.html",
            {
                "request": request,
                "name": name,
                "login": login,
                "password": password,
                "secret_origin": secret,
            },
        )


@router.post("/register")
async def register_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    name: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    secret_origin: str = Form(...),
    secret: int = Form(...),
):
    """Регистрирует пользователя при совпадении секретного числа"""

    if verify_password(str(secret), secret_origin):
        schema = UserSchema(name=name, email=login, password=password)
        if schema:
            await add_model(db=db, schema=schema, model=User)
            return templates.TemplateResponse(
                "sign_in.html", {"request": request, "register": 1}
            )
        else:
            return {"message": "Что-то пошло не так!"}
    else:
        return {"message": "Что-то пошло не так!"}


@router.get("/sign-in", response_class=HTMLResponse)
async def sign_in(request: Request):
    """Страница входа пользователя"""

    return templates.TemplateResponse("sign_in.html", {"request": request})


@router.post("/login", response_class=RedirectResponse)
async def login(
    db: Annotated[AsyncSession, Depends(get_session)],
    login: str = Form(...),
    password: str = Form(...),
):
    """Логиним пользователя и присваиваем ему jwt токен"""

    # Получаем пользователя из базы
    q = get_user_by_email(email=login)
    user = await get_model(db=db, q=q)

    # Производим валидацию пароля и пользователя, и если всё хорошо присваеваем jwt токен
    if user and verify_password(plain_password=password, hashed_password=user.password):
        access_token = create_access_token({"sub": str(user.id)})
        redirect = RedirectResponse("/main_chats", status_code=302)
        redirect.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=3600,
        )
        return redirect

    # Если валидация пользователя не прошла выводим соответствующую ошибку
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные пользователя",
        )
