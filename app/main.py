from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from app.database import engine, get_session
from app.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="TaskFlow", lifespan=lifespan)


async def get_context(session: AsyncSession = Depends(get_session)):
    return {"session": session}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "ok"}
