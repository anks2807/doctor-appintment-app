from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("INFO:     Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("INFO:     Database tables created successfully.")
    yield

    await engine.dispose()


app = FastAPI(title="Doctor Appointment API",lifespan=lifespan)