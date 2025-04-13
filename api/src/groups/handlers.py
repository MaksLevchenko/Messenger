from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession


from chats.schemas import ChatSchema
from db.models import User, ChatGroup, Chat
from .schemas import GroupSchema
from dependencies import get_auth_user, get_session
from crud.crud import add_model, get_model
from chats.querys import select_chat_by_id
from groups.querys import select_group_by_id
from users.querys import select_user_by_id


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/new_group", response_class=HTMLResponse)
async def new_group(request: Request):

    return templates.TemplateResponse("new_group.html", {"request": request})


@router.post("/add_group")
async def add_group(
    db: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    group_name: str = Form(...),
    user_auth: User = Depends(get_auth_user),
):
    """Добавляет группу в базу данных"""

    # Получаем пользователя
    q = select_user_by_id(id=int(user_auth))
    sender = await get_model(db=db, q=q)

    # Добовляем группу в базу данных:
    # Создаём чат, привязываем его к группе и добавляем в него пользователя
    schema = ChatSchema(title=f"Чат группы {group_name}", type_chat=False)
    chat_id = await add_model(db=db, schema=schema, model=Chat)
    q = select_chat_by_id(chat_id=chat_id)
    chat = await get_model(db=db, q=q)
    chat.users.append(sender)

    # Создаём группу
    schema = GroupSchema(title=group_name, owner_id=sender.id, chat_id=chat_id)
    group_id = await add_model(db=db, schema=schema, model=ChatGroup)
    q = select_group_by_id(group_id=group_id)
    group = await get_model(db=db, q=q)

    # Добавляем пользователя в группу
    group.users.append(sender)
    await db.commit()

    if sender in group.users:

        return templates.TemplateResponse(
            "add_group.html",
            {
                "request": request,
                "group": group,
                "user_id": sender.id,
            },
        )
    else:
        return templates.TemplateResponse(
            "add_group.html",
            {
                "request": request,
                "user_id": sender.id,
            },
        )


@router.post("/add_in_group")
async def add_group(
    db: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    group_id: int = Form(...),
    user_auth: User = Depends(get_auth_user),
):
    """Добавляет пользователя в группу"""

    # Получаем пользователя
    q = select_user_by_id(id=int(user_auth))
    sender = await get_model(db=db, q=q)

    # Получаем группу
    q = select_group_by_id(group_id=group_id)
    group = await get_model(db=db, q=q)

    # Добавляем пользователя в группу
    group.users.append(sender)
    await db.commit()

    if sender in group.users:

        return templates.TemplateResponse(
            "add_in_group.html",
            {
                "request": request,
                "group": group,
                "user_id": sender.id,
            },
        )
    else:
        return templates.TemplateResponse(
            "add_in_group.html",
            {
                "request": request,
                "user_id": sender.id,
            },
        )
