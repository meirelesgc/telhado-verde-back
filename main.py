from fastapi import FastAPI
from database import Base, engine
from routes import dispositivo_routes, leitura_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(dispositivo_routes.router)
app.include_router(leitura_routes.router)