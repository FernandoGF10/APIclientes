from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.medidor import Medidor
from app.models.cliente import Cliente
from app.schemas.medidor import MedidorCreate, MedidorUpdate, MedidorResponse

router = APIRouter(prefix="/api/medidores", tags=["Medidores"])


@router.get("/", response_model=list[MedidorResponse])
def listar_medidores(id_cliente: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Medidor)
    if id_cliente:
        query = query.filter(Medidor.id_cliente == id_cliente)
    return query.all()


@router.get("/{id_medidor}", response_model=MedidorResponse)
def obtener_medidor(id_medidor: int, db: Session = Depends(get_db)):
    medidor = db.query(Medidor).filter(Medidor.id_medidor == id_medidor).first()
    if not medidor:
        raise HTTPException(404, "Medidor no encontrado")
    return medidor


@router.post("/", response_model=MedidorResponse)
def crear_medidor(data: MedidorCreate, db: Session = Depends(get_db)):

    # Validar que el cliente existe
    cliente = db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first()
    if not cliente:
        raise HTTPException(400, "El cliente no existe")

    # Validar código único
    existe = db.query(Medidor).filter(Medidor.codigo_medidor == data.codigo_medidor).first()
    if existe:
        raise HTTPException(400, "El código del medidor ya está registrado")

    medidor = Medidor(**data.dict())
    db.add(medidor)
    db.commit()
    db.refresh(medidor)
    return medidor


@router.put("/{id_medidor}", response_model=MedidorResponse)
def actualizar_medidor(id_medidor: int, data: MedidorUpdate, db: Session = Depends(get_db)):
    medidor = db.query(Medidor).filter(Medidor.id_medidor == id_medidor).first()
    if not medidor:
        raise HTTPException(404, "Medidor no encontrado")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(medidor, field, value)

    db.commit()
    db.refresh(medidor)
    return medidor


@router.delete("/{id_medidor}")
def eliminar_medidor(id_medidor: int, db: Session = Depends(get_db)):
    medidor = db.query(Medidor).filter(Medidor.id_medidor == id_medidor).first()
    if not medidor:
        raise HTTPException(status_code=404, detail="Medidor no encontrado")

    db.delete(medidor)  # Esto elimina el registro físicamente
    db.commit()
    return {"message": "Medidor eliminado correctamente"}


@router.put("/{id_medidor}/estado")
def cambiar_estado_medidor(id_medidor: int, db: Session = Depends(get_db)):
    medidor = db.query(Medidor).filter(Medidor.id_medidor == id_medidor).first()
    if not medidor:
        raise HTTPException(404, "Medidor no encontrado")

    medidor.estado = not medidor.estado
    db.commit()
    return {"message": f"Estado cambiado a {'Activo' if medidor.estado else 'Inactivo'}"}
