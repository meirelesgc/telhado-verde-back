from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.leitura import Leitura
from schemas.leitura_schema import LeituraCreate, FiltroLeitura
from datetime import datetime

router = APIRouter(prefix="/leitura", tags=["Leitura"])

# INSERT
@router.post("/")
def inserir_leitura(data: LeituraCreate, db: Session = Depends(get_db)):
    if data.tipo not in ["temperatura", "umidade"]:
        raise HTTPException(400, "Tipo inválido")

    leitura = Leitura(**data.dict())
    db.add(leitura)
    db.commit()
    db.refresh(leitura)

    return {
        "status": "ok",
        "id_leitura": leitura.id
    }

# LISTAR TODAS
@router.get("/{tipo}")
def listar(tipo: str, db: Session = Depends(get_db)):
    dados = db.query(Leitura).filter(Leitura.tipo == tipo).all()

    return {
        "total": len(dados),
        "dados": dados
    }

# LISTAR POR DIA
@router.post("/filtro")
def listar_por_dia(filtro: FiltroLeitura, db: Session = Depends(get_db)):
    query = db.query(Leitura).filter(Leitura.tipo == filtro.tipo)

    if filtro.data:
        data_ini = datetime.strptime(filtro.data, "%Y-%m-%d")
        data_fim = data_ini.replace(hour=23, minute=59, second=59)

        query = query.filter(
            Leitura.criado_em.between(data_ini, data_fim)
        )

    if filtro.id_sensor:
        query = query.filter(Leitura.id_sensor == filtro.id_sensor)

    dados = query.all()

    return {
        "total": len(dados),
        "dados": dados
    }

# BUSCAR POR ID
@router.get("/{tipo}/{id}")
def buscar(tipo: str, id: int, db: Session = Depends(get_db)):
    leitura = db.query(Leitura).filter(
        Leitura.id == id,
        Leitura.tipo == tipo
    ).first()

    if not leitura:
        raise HTTPException(404, "Não encontrado")

    return leitura

# DELETE
@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    leitura = db.query(Leitura).filter(Leitura.id == id).first()

    if not leitura:
        raise HTTPException(404, "Não encontrado")

    db.delete(leitura)
    db.commit()

    return {"status": "ok"}