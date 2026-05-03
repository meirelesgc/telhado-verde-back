from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dispositivo_routes, leitura_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dispositivo_routes.router)
app.include_router(leitura_routes.router)
