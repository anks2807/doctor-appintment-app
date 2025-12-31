from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import engine
from app.db.base import Base
from app.api.v1 import users_api, doctor_api, appointment_api


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("INFO:     Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("INFO:     Database tables created successfully.")
    yield

    await engine.dispose()


app = FastAPI(title="Doctor Appointment API", lifespan=lifespan)

app.include_router(users_api.router, prefix="/api/v1", tags=["Users"])
app.include_router(doctor_api.router, prefix="/api/v1", tags=["Doctors"])
app.include_router(appointment_api.router, prefix="/api/v1", tags=["Appointments"])