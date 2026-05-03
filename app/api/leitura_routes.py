from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.leitura import Leitura
from app.schemas.leitura_schema import LeituraCreate

router = APIRouter(prefix="/leitura", tags=["Leitura"])


@router.post("/")
def inserir_leitura(data: LeituraCreate, db: Session = Depends(get_db)):
    leitura = Leitura(**data.dict())
    db.add(leitura)
    db.commit()
    db.refresh(leitura)

    return {"status": "ok", "id_leitura": leitura.id}


@router.get("/")
def listar(
    tipo: Optional[str] = None,
    data: Optional[str] = None,
    id_sensor: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Leitura)

    if tipo:
        query = query.filter(Leitura.tipo == tipo)

    if data:
        data_ini = datetime.strptime(data, "%Y-%m-%d")
        data_fim = data_ini.replace(hour=23, minute=59, second=59)
        query = query.filter(Leitura.criado_em.between(data_ini, data_fim))

    if id_sensor:
        query = query.filter(Leitura.id_sensor == id_sensor)

    total = query.count()
    dados = query.offset(skip).limit(limit).all()

    return {"total": total, "dados": dados}


@router.get("/agregacao/ultima-leitura")
def ultima_leitura_sensores(db: Session = Depends(get_db)):
    subquery = (
        db.query(Leitura.id_sensor, func.max(Leitura.criado_em).label("ultima_leitura"))
        .group_by(Leitura.id_sensor)
        .subquery()
    )

    resultados = (
        db.query(Leitura)
        .join(
            subquery,
            (Leitura.id_sensor == subquery.c.id_sensor)
            & (Leitura.criado_em == subquery.c.ultima_leitura),
        )
        .all()
    )

    return resultados


@router.get("/agregacao/estatisticas")
def estatisticas(
    tipo: Optional[str] = None,
    id_sensor: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(
        Leitura.id_sensor,
        func.min(Leitura.valor).label("minimo"),
        func.max(Leitura.valor).label("maximo"),
        func.avg(Leitura.valor).label("media"),
        func.count(Leitura.id).label("total"),
    )

    if tipo:
        query = query.filter(Leitura.tipo == tipo)

    if id_sensor:
        query = query.filter(Leitura.id_sensor == id_sensor)

    resultados = query.group_by(Leitura.id_sensor).all()

    retorno = []
    for r in resultados:
        retorno.append(
            {
                "id_sensor": r.id_sensor,
                "minimo": r.minimo,
                "maximo": r.maximo,
                "media": round(r.media, 2) if r.media else 0,
                "total_leituras": r.total,
            }
        )

    return retorno


@router.get("/{id}")
def buscar(id: int, db: Session = Depends(get_db)):
    leitura = db.query(Leitura).filter(Leitura.id == id).first()

    if not leitura:
        raise HTTPException(404, "Nao encontrado")

    return leitura


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    leitura = db.query(Leitura).filter(Leitura.id == id).first()

    if not leitura:
        raise HTTPException(404, "Nao encontrado")

    db.delete(leitura)
    db.commit()

    return {"status": "ok"}
