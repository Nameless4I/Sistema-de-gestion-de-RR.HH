from pydantic import BaseModel
from datetime import date

class FeriadoResponse(BaseModel):
    id: int
    fecha: date
    descripcion: str

    class Config:
        from_attributes = True