import smtplib

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from typing import Annotated, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from messages.querys import select_message_by_id
from chats.querys import select_chat_by_id, select_chat_by_ids
from users.querys import select_user_by_id
from messages import MessageSchema
from crud.crud import add_model, get_model
from dependencies import get_session, send_email
from chats import ChatSchema
from db.models import Chat, Message


router = APIRouter(prefix="/ws/chat")


class ConnectionManager:

    def __init__(self):
        # Хранение активных соединений в виде {room_id: {user_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: int):
        """
        Устанавливает соединение с пользователем.
        websocket.accept() — подтверждает подключение.
        """
        await websocket.accept()

        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {}
        self.active_connections[chat_id][user_id] = websocket

    def disconnect(self, chat_id: int, user_id: int):
        """
        Закрывает соединение и удаляет его из списка активных подключений.
        Если в комнате больше нет пользователей, удаляет комнату.
        """
        if (
            chat_id in self.active_connections
            and user_id in self.active_connections[chat_id]
        ):
            del self.active_connections[chat_id][user_id]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, message: str, chat_id: int, sender_id: int):
        """
        Рассылает сообщение всем пользователям в комнате.
        """
        if chat_id in self.active_connections:
            for user_id, connection in self.active_connections[chat_id].items():
                message_with_class = {"text": message, "is_self": user_id == sender_id}
                await connection.send_json(message_with_class)


manager = ConnectionManager()


@router.websocket("/{chat_id}/{user_id}/{user_auth}")
async def websocket_endpoint(
    db: Annotated[AsyncSession, Depends(get_session)],
    websocket: WebSocket,
    chat_id: int,
    user_id: int,
    user_auth: int,
    username: str,
):
    """Подключение к вебсокету"""

    # Получаем данные пользователей
    q = select_user_by_id(id=user_auth)
    sender = await get_model(db=db, q=q)
    q = select_user_by_id(id=user_id)
    recipient = await get_model(db=db, q=q)

    # Проверяем передан ли id чата
    if not chat_id:

        # Даже если id чата не передан, проверяем существует ли чат где присутствуют оба пользователя и это не групповой чат
        q = select_chat_by_ids(user_ids=(sender.id, recipient.id))
        chat = await get_model(db=db, q=q)

        # Проверяем, что такого чата точно нет
        if not chat:

            # Создаём чат
            schema = ChatSchema(
                title=f"{sender.name.split()[0]} {recipient.name.split()[0]}",
                type_chat=True,
            )
            chat_id = await add_model(db=db, schema=schema, model=Chat)
            q = select_chat_by_id(chat_id=chat_id)
            chat = await get_model(db=db, q=q)

            # Добавляем пользователей в новый чат
            chat.users.append(sender)
            chat.users.append(recipient)
            await db.commit()
    else:

        # Если id чата переден, получаем этот чат
        q = select_chat_by_id(chat_id=chat_id)
        chat = await get_model(db=db, q=q)

    # Проверяем что чат личный
    if chat.type_chat:

        # Подключаемся к вебсокету
        await manager.connect(websocket, chat.id, user_id)

        # Выводим все сообщения чата из базы
        for message in chat.messages:
            await manager.broadcast(
                f"{message.sender.name} (ID: {message.sender_id}) {message.text}",
                chat.id,
                user_id if message.sender.id == user_auth else user_auth,
            )

        # Выводим информационное сообщение о присоединении пользователя к чату и сразу записываем его в базу
        data = f"{sender.name} (ID: {user_auth}) присоединился к чату."
        schema = MessageSchema(
            text=" ".join(data.split()[3::]), chat_id=chat.id, sender_id=user_auth
        )
        message_id = await add_model(db=db, schema=schema, model=Message)
        q = select_message_by_id(message_id=message_id)
        new_message = await get_model(db=db, q=q)
        await manager.broadcast(
            data,
            chat.id,
            user_id,
        )

        # Проверяем присутствует ли в чате получатель сообщения,
        #  если присутствует, присваиваем сообщению статус прочтённого, если нет,
        #  отправляем сообщение получателю по его email
        if len(manager.active_connections[chat.id]) == 2:
            new_message.status = True
            await db.commit()
        else:
            send_email(
                address=recipient.email,
                text=f"{recipient.name} у вас есть непрочитанное сообщение от пользователя {sender.name} в MaksiGram".encode(
                    "utf8"
                ),
            )

    # Определяем действия, если чат групповой
    else:

        # Подключаемся к вебсокету
        await manager.connect(websocket, chat.id, user_id)

        # Выводим все сообщения чата из базы
        for message in chat.messages:
            await manager.broadcast(
                f"{message.sender.name} (ID: {message.sender_id}) {message.text}",
                chat.id,
                message.sender_id,
            )

        # Выводим информационное сообщение о присоединении пользователя к чату и сразу записываем его в базу
        data = f"{sender.name} (ID: {user_auth}) присоединился к чату."
        schema = MessageSchema(
            text=" ".join(data.split()[3::]), chat_id=chat.id, sender_id=user_auth
        )
        await add_model(db=db, schema=schema, model=Message)
        await manager.broadcast(
            data,
            chat.id,
            user_id,
        )

    try:

        # Запускаем бесконечный цикл для работы вебсокета
        while True:
            data = await websocket.receive_text()
            schema = MessageSchema(text=data, chat_id=chat.id, sender_id=user_auth)
            await add_model(db=db, schema=schema, model=Message)
            await manager.broadcast(
                f"{sender.name} (ID: {user_auth}): {data}", chat.id, user_id
            )
            # Проверяем присутствует ли в чате получатель сообщения,
            #  если присутствует, присваиваем сообщению статус прочтённого, если нет,
            #  отправляем сообщение получателю по его email
            if len(manager.active_connections[chat.id]) == 2:
                new_message.status = True
                await db.commit()
            else:
                send_email(
                    address=recipient.email,
                    text=f"{recipient.name} у вас есть непрочитанное сообщение от пользователя {sender.name} в MaksiGram".encode(
                        "utf8"
                    ),
                )

    # При выходе пользователя из чата разрываем соединение и выводим информационное сообщение, которое сразу записываем в базу
    except WebSocketDisconnect:
        manager.disconnect(chat.id, user_id)
        data = f"{sender.name} (ID: {user_auth}) покинул чат."
        schema = MessageSchema(
            text=" ".join(data.split()[3::]), chat_id=chat.id, sender_id=user_auth
        )
        await add_model(db=db, schema=schema, model=Message)
        await manager.broadcast(
            data,
            chat.id,
            user_id,
        )
