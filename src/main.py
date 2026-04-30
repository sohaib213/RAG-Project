from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
from routes import base_router, data_router, nlp_router
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDBFactory import VectorDBFactory
from stores.llm.tempelate.template_parser import TemplateParser


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs once when the app starts
    settings = get_settings()

    # Connect to MongoDB
    app.db_motor_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client = app.db_motor_client[settings.MONGODB_DB_NAME]

    # Create LLM clients using the factory
    llm_factory = LLMFactory()
    app.generation_client = llm_factory.create_generation_client()
    app.embedding_client = llm_factory.create_embedding_client()

    # Create vector DB client using the factory
    vectordb_factory = VectorDBFactory()
    app.vectordb_client = vectordb_factory.create_client()

    # Create the template parser for prompts
    app.template_parser = TemplateParser(language="en")

    yield

    # This runs when the app shuts down
    app.db_motor_client.close()


def create_app():
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )

    # Register all routers with their URL prefixes
    app.include_router(base_router, prefix="/api")
    app.include_router(data_router, prefix="/api/data")
    app.include_router(nlp_router, prefix="/api/nlp")

    return app


app = create_app()