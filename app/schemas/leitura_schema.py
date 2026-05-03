from typing import Optional

from pydantic import BaseModel


class LeituraCreate(BaseModel):
    tipo: str
    id_sensor: int
    id_dispositivo: int
    valor: float


class FiltroLeitura(BaseModel):
    tipo: str
    data: Optional[str] = None
    id_sensor: Optional[int] = None
