from pydantic import BaseModel

class DispositivoCreate(BaseModel):
    nome: str
    latitude: float
    longitude: float