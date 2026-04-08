from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from starlette.responses import JSONResponse, HTMLResponse

from app.api.v1.routers.admin import admin_router
from app.exceptions.base import AppException

from fastapi.templating import Jinja2Templates

from app.api.v1.routers.operations import operations_router
from app.api.v1.routers.users import users_router
from app.api.v1.routers.wallets import wallets_router
from app.database import engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/", include_in_schema=False)
async def web_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(wallets_router)
app.include_router(operations_router)
app.include_router(users_router)
app.include_router(admin_router)