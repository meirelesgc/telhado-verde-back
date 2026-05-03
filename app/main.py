from fastapi import FastAPI

from app.api import dispositivo_routes, leitura_routes

app = FastAPI()

app.include_router(dispositivo_routes.router)
app.include_router(leitura_routes.router)
