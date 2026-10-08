from fastapi import FastAPI

from src.api.routers.ask import router as ask_router
from src.api.routers.auth import router as auth_router
from src.api.routers.health import router as health_router
from src.infrastructure.config import load_settings_from_environ

app = FastAPI(title="Domain Copilot")
app.state.settings = load_settings_from_environ()
app.include_router(auth_router)
app.include_router(ask_router)
app.include_router(health_router)
