import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from config.settings import settings
from config.loger_config import loger_init

from groups.handlers import router as router_group
from users.handlers import router as router_user
from websocket.websocket import router as router_websocket
from chats.handlers import router as router_chat


loger_init()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MaksiGram",
    version=settings.app_version,
    redoc_url=None,
    docs_url=settings.app_swagger_url,
    root_path=settings.app_root_path,
)

app.mount("/static", StaticFiles(directory="static"), "static")


@app.get("/")
async def healthcheck():
    return {
        "title": app.title,
        "version": app.version,
    }


app.include_router(router_websocket, tags=["Websocket"])
app.include_router(router_chat, tags=["Чаты"])
app.include_router(router_group, tags=["Группы"])
app.include_router(router_user, tags=["Пользователь"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
