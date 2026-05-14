from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routes.departments import router as main_router
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=settings.app_description,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(main_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running. Go to /docs for Swagger UI"}
