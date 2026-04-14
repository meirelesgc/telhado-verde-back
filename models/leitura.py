from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String
from datetime import datetime
from database import Base

class Leitura(Base):
    __tablename__ = "leitura"

    id = Column(Integer, primary_key=True, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    tipo = Column(String(20))  # temperatura | umidade
    id_sensor = Column(Integer)
    id_dispositivo = Column(Integer, ForeignKey("dispositivo.id"))

    valor = Column(Float)