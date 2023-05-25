import os
import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.responses import RedirectResponse
from config import settings
from openapi import init_openAPI
from routers import router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    try:
        app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
    else:
        logger.info("Connected to MongoDB")
    try:
        redis = await aioredis.from_url(settings.REDIS_DB)
        app.redis = redis
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
    else:
        logger.info("Connected to Redis")


@app.on_event("shutdown")
async def shutdown():
    try:
        app.mongodb_client.close()
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
    else:
        logger.info("Closed MongoDB connection")
    try:
        app.redis.close()
        await app.redis.wait_closed()
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
    else:
        logger.info("Closed Redis connection")


@app.get("/", include_in_schema=False)
async def get_root():
    if (root_url := os.getenv("ROOT_URL")) is None:
        return {
            "api_docs": {"openapi": f"{root_url}/docs", "redoc": f"{root_url}/redoc"}
        }
    response = RedirectResponse(url=f"{root_url}/docs")
    return response


app.include_router(router, tags=["Todo"], prefix="/api/v1/task")

init_openAPI(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
