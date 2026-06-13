from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Date, cast, func
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
    id_dispositivo: Optional[int] = None,
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

    if id_dispositivo:
        query = query.filter(Leitura.id_dispositivo == id_dispositivo)

    total = query.count()
    dados = query.offset(skip).limit(limit).all()

    return {"total": total, "dados": dados}


@router.get("/agregacao/ultima-leitura")
def ultima_leitura_sensores(
    id_dispositivo: Optional[int] = None, db: Session = Depends(get_db)
):
    base_query = db.query(
        Leitura.id_sensor, func.max(Leitura.criado_em).label("ultima_leitura")
    )

    if id_dispositivo:
        base_query = base_query.filter(Leitura.id_dispositivo == id_dispositivo)

    subquery = base_query.group_by(Leitura.id_sensor).subquery()

    resultados_query = db.query(Leitura).join(
        subquery,
        (Leitura.id_sensor == subquery.c.id_sensor)
        & (Leitura.criado_em == subquery.c.ultima_leitura),
    )

    if id_dispositivo:
        resultados_query = resultados_query.filter(
            Leitura.id_dispositivo == id_dispositivo
        )

    return resultados_query.all()


@router.get("/agregacao/estatisticas")
def estatisticas(
    tipo: Optional[str] = None,
    id_sensor: Optional[int] = None,
    id_dispositivo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(
        Leitura.id_sensor,
        Leitura.id_dispositivo,
        func.min(Leitura.valor).label("minimo"),
        func.max(Leitura.valor).label("maximo"),
        func.avg(Leitura.valor).label("media"),
        func.count(Leitura.id).label("total"),
    )

    if tipo:
        query = query.filter(Leitura.tipo == tipo)

    if id_sensor:
        query = query.filter(Leitura.id_sensor == id_sensor)

    if id_dispositivo:
        query = query.filter(Leitura.id_dispositivo == id_dispositivo)

    resultados = query.group_by(Leitura.id_sensor, Leitura.id_dispositivo).all()

    retorno = []
    for r in resultados:
        retorno.append({
            "id_sensor": r.id_sensor,
            "id_dispositivo": r.id_dispositivo,
            "minimo": r.minimo,
            "maximo": r.maximo,
            "media": round(r.media, 2) if r.media else 0,
            "total_leituras": r.total,
        })

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


@router.get("/agregacao/media-movel")
def media_movel(
    tipo: str,
    data_inicio: str,
    data_fim: str,
    intervalo_minutos: int = Query(30, ge=15, le=1440),
    id_dispositivo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    query = db.query(Leitura).filter(
        Leitura.tipo == tipo, Leitura.criado_em.between(dt_inicio, dt_fim)
    )

    if id_dispositivo:
        query = query.filter(Leitura.id_dispositivo == id_dispositivo)

    leituras = query.order_by(Leitura.criado_em).all()

    if not leituras:
        return []

    resultado = []
    tempo_atual = leituras[0].criado_em
    tempo_limite = tempo_atual + timedelta(minutes=intervalo_minutos)
    soma = 0
    contagem = 0

    for l in leituras:
        if l.criado_em < tempo_limite:
            soma += l.valor
            contagem += 1
        else:
            if contagem > 0:
                resultado.append({
                    "inicio_janela": tempo_atual,
                    "fim_janela": tempo_limite,
                    "media": round(soma / contagem, 2),
                })
            tempo_atual = l.criado_em
            tempo_limite = tempo_atual + timedelta(minutes=intervalo_minutos)
            soma = l.valor
            contagem = 1

    if contagem > 0:
        resultado.append({
            "inicio_janela": tempo_atual,
            "fim_janela": tempo_limite,
            "media": round(soma / contagem, 2),
        })

    return resultado


@router.get("/agregacao/amplitude-termica")
def amplitude_termica(
    data_inicio: str,
    data_fim: str,
    id_dispositivo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    query = db.query(
        cast(Leitura.criado_em, Date).label("data"),
        func.max(Leitura.valor).label("maximo"),
        func.min(Leitura.valor).label("minimo"),
    ).filter(
        Leitura.tipo == "temperatura", Leitura.criado_em.between(dt_inicio, dt_fim)
    )

    if id_dispositivo:
        query = query.filter(Leitura.id_dispositivo == id_dispositivo)

    resultados = query.group_by(cast(Leitura.criado_em, Date)).all()

    return [
        {
            "data": r.data,
            "maximo": r.maximo,
            "minimo": r.minimo,
            "amplitude": round(r.maximo - r.minimo, 2),
        }
        for r in resultados
    ]


@router.get("/agregacao/taxa-desidratacao")
def taxa_desidratacao(
    data_inicio: str,
    data_fim: str,
    id_dispositivo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    query = db.query(Leitura).filter(
        Leitura.tipo == "umidade", Leitura.criado_em.between(dt_inicio, dt_fim)
    )

    if id_dispositivo:
        query = query.filter(Leitura.id_dispositivo == id_dispositivo)

    leituras = query.order_by(Leitura.criado_em).all()

    agrupamento_por_dia = {}
    for l in leituras:
        dia_str = l.criado_em.date().isoformat()
        if dia_str not in agrupamento_por_dia:
            agrupamento_por_dia[dia_str] = []
        agrupamento_por_dia[dia_str].append(l)

    resultado = []
    for dia, registros in agrupamento_por_dia.items():
        if len(registros) >= 2:
            reg_inicial = registros[0]
            reg_final = registros[-1]
            delta_umidade = reg_final.valor - reg_inicial.valor
            horas_decorridas = (
                reg_final.criado_em - reg_inicial.criado_em
            ).total_seconds() / 3600

            taxa_por_hora = (
                delta_umidade / horas_decorridas if horas_decorridas > 0 else 0
            )

            resultado.append({
                "data": dia,
                "umidade_inicial": reg_inicial.valor,
                "umidade_final": reg_final.valor,
                "delta_umidade": round(delta_umidade, 2),
                "horas_decorridas": round(horas_decorridas, 2),
                "taxa_por_hora": round(taxa_por_hora, 2),
            })

    return resultado
