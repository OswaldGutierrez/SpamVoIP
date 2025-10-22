from sqlalchemy import Column, Integer, String, Date, Text, JSON, TIMESTAMP, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class NumeroSpam(Base):
    __tablename__ = "numerosspam"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(32), unique=True, nullable=False)
    quienagrego = Column(String(100))
    fecharegistro = Column(DateTime(timezone=True), server_default=func.now())
    nota = Column(Text)


class ConteoSpam(Base):
    __tablename__ = "conteospam"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(32), nullable=False)
    fecha = Column(Date, nullable=False)
    cantidad = Column(Integer, default=0)


class EventoSpam(Base):
    __tablename__ = "eventosspam"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(32))
    tipoevento = Column(String(32))
    fuente = Column(String(64))
    detalles = Column(JSON)
    fechahora = Column(DateTime(timezone=True), default=datetime.now)
