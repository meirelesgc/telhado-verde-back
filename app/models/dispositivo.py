from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.database import Base


class Dispositivo(Base):
    __tablename__ = "dispositivo"

    id = Column(Integer, primary_key=True, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    nome = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
