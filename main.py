from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_analytics.fastapi import Analytics
import uvicorn

from app.routers import router, redirect_router
from app import models
from core.config import settings
from core.db import engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener App",
    description="Sample FastAPI Application with Swagger and Sqlalchemy",
    version="1.0.0",)

app.add_middleware(Analytics, api_key='6e34dff8-f5f2-4544-98e9-83da407a8252') 


app.include_router(router, prefix="/api/v1")
app.include_router(redirect_router, prefix="")


if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)