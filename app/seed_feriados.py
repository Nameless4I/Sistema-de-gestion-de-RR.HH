from app.database import SessionLocal, Base, engine
from app.models import usuario, empleado, departamento, cargo, asistencia, vacacion, feriado
from app.models.feriado import Feriado
from datetime import date

# Crear la tabla si no existe
Base.metadata.create_all(bind=engine)

FERIADOS_2026 = [
    (date(2026, 1, 1),  "Año Nuevo"),
    (date(2026, 4, 2),  "Jueves Santo"),
    (date(2026, 4, 3),  "Viernes Santo"),
    (date(2026, 4, 5),  "Domingo de Resurrección"),
    (date(2026, 5, 1),  "Día del Trabajador"),
    (date(2026, 6, 7),  "Batalla de Arica"),
    (date(2026, 6, 29), "San Pedro y San Pablo"),
    (date(2026, 7, 23), "Día de la Fuerza Aérea"),
    (date(2026, 7, 28), "Día de la Independencia"),
    (date(2026, 7, 29), "Día de la Independencia Nacional (2do día)"),
    (date(2026, 8, 6),  "Batalla de Junín"),
    (date(2026, 8, 30), "Santa Rosa de Lima"),
    (date(2026, 10, 8), "Combate de Angamos"),
    (date(2026, 11, 1), "Día de Todos los Santos"),
    (date(2026, 12, 8), "Inmaculada Concepción"),
    (date(2026, 12, 9), "Batalla de Ayacucho"),
    (date(2026, 12, 25), "Navidad"),
]

def crear_feriados_2026():
    db = SessionLocal()
    try:
        existentes = db.query(Feriado).count()
        if existentes > 0:
            print(f"Ya existen {existentes} feriados registrados.")
            return

        for fecha, descripcion in FERIADOS_2026:
            db.add(Feriado(fecha=fecha, descripcion=descripcion))

        db.commit()
        print(f"✓ {len(FERIADOS_2026)} feriados de 2026 registrados correctamente.")
    finally:
        db.close()

if __name__ == "__main__":
    crear_feriados_2026()