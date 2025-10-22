from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, NumeroSpam, EventoSpam
import datetime


# CREAR TABLAS
Base.metadata.create_all(bind=engine)


# DEPENDENCIA DE DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MODELOS Pydantic - Para validar el formato de los datos antes de procesarlos
class NumeroSpamIn(BaseModel):
    numero: str
    nota: str = None
    quienagrego: str = "sistema"

class EventoIn(BaseModel):
    numero: str
    tipoevento: str
    fuente: str
    detalles: dict | None = None


# FASTAPI
app = FastAPI(title="Sistema de detección de llamadas SPAM")


# ENDPOINTS
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    numeros = db.query(NumeroSpam).all()
    return [
        {
            "id": n.id,
            "numero": n.numero,
            "nota": n.nota,
            "quienagrego": n.quienagrego,
            "fecharegistro": n.fecharegistro,
        }
        for n in numeros
    ]


@app.get("/verificar-numero")
def verificar_numero(numero: str = Query(...), db: Session = Depends(get_db)):
    numero_normalizado = numero.strip()
    spam = db.query(NumeroSpam).filter(NumeroSpam.numero == numero_normalizado).first()
    if spam:
        return {
            "numero": spam.numero,
            "es_spam": True,
            "nota": spam.nota,
            "quien_agrego": spam.quienagrego,
            "fecha_registro": spam.fecharegistro,
        }
    return {"numero": numero_normalizado, "es_spam": False}


@app.post("/agregar-numero")
def agregar_numero(data: NumeroSpamIn, db: Session = Depends(get_db)):
    existente = db.query(NumeroSpam).filter(NumeroSpam.numero == data.numero).first()
    if existente:
        raise HTTPException(status_code=400, detail="El número ya está registrado como SPAM")

    nuevo = NumeroSpam(
        numero=data.numero,
        nota=data.nota,
        quienagrego=data.quienagrego,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Número agregado como SPAM", "id": nuevo.id}


@app.delete("/eliminar-numero")
def eliminar_numero(numero: str = Query(...), db: Session = Depends(get_db)):
    numero_obj = db.query(NumeroSpam).filter(NumeroSpam.numero == numero).first()
    if not numero_obj:
        raise HTTPException(status_code=404, detail="Número no encontrado")

    db.delete(numero_obj)
    db.commit()
    return {"mensaje": "Número eliminado correctamente"}


@app.post("/registrar-evento")
def registrar_evento(data: EventoIn, db: Session = Depends(get_db)):
    evento = EventoSpam(
        numero=data.numero,
        tipoevento=data.tipoevento,
        fuente=data.fuente,
        detalles=data.detalles,
        fechahora=datetime.datetime.now()
    )
    db.add(evento)
    db.commit()
    return {"mensaje": "Evento registrado"}



# INTEGRACIÓN FUTURA CON ISSABEL - Solamente es la lógica (Todavía no he hecho la integración con isabel)
@app.get("/issabel-hook")
def issabel_hook(numero: str, db: Session = Depends(get_db)):
    spam = db.query(NumeroSpam).filter(NumeroSpam.numero == numero).first()
    if spam:
        return {"accion": "redirigir", "a_numero_virtual": "6000", "motivo": spam.nota}
    return {"accion": "permitir", "motivo": "Número no identificado como SPAM"}
