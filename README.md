#  Sistema de Gestión de RRHH

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue?logo=postgresql)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

Sistema web completo de gestión de Recursos Humanos con API REST, autenticación JWT y control de acceso por roles. Desarrollado con Python (FastAPI) + JavaScript + PostgreSQL.

---

## ¿Qué hace este sistema?

Permite a una empresa gestionar su personal de forma digital:
- Registrar empleados, departamentos y cargos
- Controlar asistencia diaria (entrada/salida con cálculo automático de horas)
- Gestionar solicitudes de vacaciones con flujo de aprobación
- Todo con acceso controlado según el rol del usuario

---

## Características principales

- **API REST completa** con 25+ endpoints documentados automáticamente (Swagger/OpenAPI)
- **Autenticación JWT** con tokens Bearer
- **5 roles de usuario** con permisos diferenciados: ADMIN, RRHH, JEFE, EMPLEADO, CONSULTOR
- **Control de acceso por scope**: un JEFE solo ve su propio equipo; un EMPLEADO solo ve sus propios datos
- **Cálculo automático** de horas trabajadas, horas extras y estado de tardanza (límite: 8:15 AM)
- **Flujo de aprobación** de vacaciones con descuento/devolución automática de días disponibles
- **Registro manual de asistencia** para correcciones (RRHH)
- **Soft delete**: empleados y departamentos nunca se eliminan, solo se desactivan

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL 18 + SQLAlchemy ORM |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| Validación | Pydantic v2 |
| Servidor | Uvicorn |

---

## Modelo de datos

6 tablas relacionadas:

```
usuarios ──── empleados ──── departamentos
                  │               │
               asistencias    (jefe_id)
                  │
              vacaciones
                  │
               cargos
```

---

## Instalación local

### Requisitos
- Python 3.10+
- PostgreSQL 14+
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-rrhh.git
cd sistema-rrhh

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Copia el archivo de ejemplo y edítalo:
cp .env.example .env
# Edita .env con tus datos de PostgreSQL y una SECRET_KEY segura

# 5. Crear la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE rrhh_db;"

# 6. Levantar el servidor (crea las tablas automáticamente)
uvicorn app.main:app --reload

# 7. Crear el usuario ADMIN inicial
python -m app.seed
```

### Acceder a la documentación
```
http://127.0.0.1:8000/docs
```

---

## Usuario inicial

| Email | Password | Rol |
|---|---|---|
| admin@empresa.com | admin | ADMIN |

> ⚠️ Cambia la contraseña del admin en producción.

---

##  Módulos y endpoints

###  Auth
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/auth/register | Crear usuario | ADMIN, RRHH |
| POST | /api/auth/login | Iniciar sesión | Público |
| GET | /api/auth/me | Perfil actual | Autenticado |

###  Departamentos
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/departamentos | Listar | Autenticado |
| GET | /api/departamentos/{id} | Obtener | Autenticado |
| POST | /api/departamentos | Crear | ADMIN |
| PUT | /api/departamentos/{id} | Editar | ADMIN |
| DELETE | /api/departamentos/{id} | Desactivar | ADMIN |

###  Cargos
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/cargos | Listar | Autenticado |
| GET | /api/cargos/{id} | Obtener | Autenticado |
| POST | /api/cargos | Crear | ADMIN |
| PUT | /api/cargos/{id} | Editar | ADMIN |

###  Empleados
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/empleados | Listar | ADMIN, RRHH, JEFE*, CONSULTOR** |
| GET | /api/empleados/{id} | Obtener | ADMIN, RRHH, JEFE*, EMPLEADO*** |
| POST | /api/empleados | Crear | ADMIN, RRHH |
| PUT | /api/empleados/{id} | Editar completo | ADMIN, RRHH |
| PATCH | /api/empleados/{id}/contacto | Editar contacto propio | EMPLEADO |
| PATCH | /api/empleados/{id}/cese | Cesar empleado | ADMIN, RRHH |

> *JEFE: solo su departamento | **CONSULTOR: sin salario ni documento | ***EMPLEADO: solo su propio registro

###  Asistencias
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/asistencias/marcar-entrada | Marcar entrada | EMPLEADO |
| PATCH | /api/asistencias/marcar-salida | Marcar salida | EMPLEADO |
| POST | /api/asistencias/manual | Crear manual | ADMIN, RRHH |
| GET | /api/asistencias | Listar | Autenticado* |
| GET | /api/asistencias/{id} | Obtener | Autenticado* |
| PATCH | /api/asistencias/{id}/justificar | Justificar | ADMIN, RRHH |

###  Vacaciones
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/vacaciones | Solicitar | EMPLEADO |
| GET | /api/vacaciones | Listar | Autenticado* |
| GET | /api/vacaciones/{id} | Obtener | Autenticado* |
| PATCH | /api/vacaciones/{id}/aprobar | Aprobar | ADMIN, RRHH, JEFE |
| PATCH | /api/vacaciones/{id}/rechazar | Rechazar | ADMIN, RRHH, JEFE |
| PATCH | /api/vacaciones/{id}/cancelar | Cancelar | EMPLEADO |

---

##  Roles y permisos

| Rol | Descripción |
|---|---|
| ADMIN | Control total del sistema |
| RRHH | Gestión de personal, asistencia y aprobación de vacaciones |
| JEFE | Supervisor de su departamento (scope limitado) |
| EMPLEADO | Acceso solo a sus propios datos |
| CONSULTOR | Solo lectura, sin datos sensibles (salario, documento) |

---

##  Notas técnicas

- Se fijó `bcrypt==4.0.1` por incompatibilidad conocida entre `passlib` y versiones más recientes de bcrypt (4.1+)
- `Base.metadata.create_all()` crea las tablas automáticamente al iniciar el servidor. Para modificaciones de esquema en producción, se recomienda implementar migraciones con **Alembic** (roadmap)
- El primer usuario ADMIN se crea vía `seed.py` ya que no existe registro previo para autenticarse

---

##  Roadmap (próximas funcionalidades)

- [ ] Módulo de Nómina (cálculo mensual, bonos, descuentos)
- [ ] Módulo de Evaluaciones de Desempeño
- [ ] Módulo de Capacitaciones
- [ ] Historial laboral de empleados
- [ ] Notificaciones (email al aprobar/rechazar vacaciones)
- [ ] Migraciones con Alembic
- [ ] Tests automatizados con pytest
- [ ] Frontend en JavaScript
- [ ] CI/CD con GitHub Actions
- [ ] Dockerización

---

##  Autor

**Jose Aldair Coronado Nalvarte**
Ingeniero Electrónico — Universidad Nacional José Faustino Sánchez Carrión

