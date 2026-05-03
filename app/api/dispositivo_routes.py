from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.dispositivo import Dispositivo
from app.schemas.dispositivo_schema import DispositivoCreate

router = APIRouter(prefix="/dispositivo", tags=["Dispositivo"])


@router.post("/")
def inserir_dispositivo(data: DispositivoCreate, db: Session = Depends(get_db)):
    novo = Dispositivo(**data.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {"status": "ok", "id_dispositivo": novo.id}
