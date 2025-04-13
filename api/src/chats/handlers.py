from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession


from db.models.users import User
from dependencies import Pagination, get_auth_user, get_session
from crud.crud import get_model, get_models

from groups.querys import select_all_groups_cards, select_user_groups_cards

from chats.querys import select_chat_cards
from users.querys import select_user_by_id, select_users_cards


# Определяем директорию с html-шаблонами и создаём объект роутера
templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/main_chats")
async def select_chat(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
    pg: Annotated[Pagination, Depends(Pagination)],
    user_auth: User = Depends(get_auth_user),
):
    """Страница с чатами"""

    # Получаем пользователя
    q = select_user_by_id(id=int(user_auth))
    sender = await get_model(db=db, q=q)

    # Получаем всех пользователей
    count, q = select_users_cards(user_id=sender.id)
    users = await get_models(db=db, pg=pg, count=count, q=q)

    # Получаем чаты пользователя
    count, q = select_chat_cards(user_id=sender.id)
    chats = await get_models(db=db, pg=pg, count=count, q=q)
    chats = set(chat for chat in chats["cards"])

    # Получаем все группы
    count, q = select_all_groups_cards()
    all_groups = await get_models(db=db, pg=pg, count=count, q=q)
    all_groups = set(group for group in all_groups["cards"])

    # Получаем группы в которых состоит пользователь
    count, q = select_user_groups_cards(user_id=sender.id)
    user_groups = await get_models(db=db, pg=pg, count=count, q=q)
    user_groups = set(group for group in user_groups["cards"])

    chats = [
        (chat, [user.id for user in chat.users if user.id != sender.id])
        for chat in chats
        if chat.type_chat
    ]
    groups_users = [
        (group, group.chat, [user.id for user in group.users]) for group in user_groups
    ]
    all_groups = [
        (group, group.chat, [user.id for user in group.users]) for group in all_groups
    ]
    recipients = [chat[1][0] for chat in chats]
    return templates.TemplateResponse(
        "chats.html",
        {
            "request": request,
            "username": sender.name,
            "user_id": sender.id,
            "users": users["cards"],
            "recipients": recipients,
            "chats": chats,
            "groups_users": groups_users,
            "all_groups": all_groups,
        },
    )


@router.post("/main_chats/join_chat", response_class=HTMLResponse)
async def join_chat(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: int = Form(...),
    chat_id: int | None = Form(...),
    user_auth: User = Depends(get_auth_user),
):
    """Подготавливаем данные для подключения к вебсокету"""

    # Получаем нужных пользователей
    q = select_user_by_id(id=int(user_auth))
    user = await get_model(db=db, q=q)
    q = select_user_by_id(id=user_id)
    recipient = await get_model(db=db, q=q)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat_id": chat_id,
            "user_id": user_id,
            "user_auth": user.id,
            "username": recipient.name,
        },
    )
