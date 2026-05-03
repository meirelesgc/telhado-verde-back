from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/")
def listar_dispositivos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dispositivos = db.query(Dispositivo).offset(skip).limit(limit).all()
    return dispositivos


@router.get("/{id_dispositivo}")
def obter_dispositivo(id_dispositivo: int, db: Session = Depends(get_db)):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == id_dispositivo).first()
    if not dispositivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return dispositivo


@router.put("/{id_dispositivo}")
def atualizar_dispositivo(
    id_dispositivo: int, data: DispositivoCreate, db: Session = Depends(get_db)
):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == id_dispositivo).first()
    if not dispositivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for key, value in data.dict().items():
        setattr(dispositivo, key, value)

    db.commit()
    db.refresh(dispositivo)
    return dispositivo


@router.delete("/{id_dispositivo}")
def deletar_dispositivo(id_dispositivo: int, db: Session = Depends(get_db)):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == id_dispositivo).first()
    if not dispositivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(dispositivo)
    db.commit()
    return {"status": "ok"}
