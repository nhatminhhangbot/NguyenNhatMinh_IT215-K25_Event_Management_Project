from fastapi import FastAPI
from app.core.exceptions import create_exception_handlers
from app.db.database import Base, engine
from app.models import user, event, event_task
from app.routers import health_router, auth_router, users_router, event_router, event_task_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")

create_exception_handlers(app)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(event_router)
app.include_router(event_task_router)
