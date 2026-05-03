from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.db.database import Base


class Leitura(Base):
    __tablename__ = "leitura"

    id = Column(Integer, primary_key=True, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(20))
    id_sensor = Column(Integer)
    id_dispositivo = Column(Integer, ForeignKey("dispositivo.id"))
    valor = Column(Float)
