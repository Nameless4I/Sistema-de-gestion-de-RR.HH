# 🏢 Sistema de Gestión de RRHH

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Tests](https://img.shields.io/badge/Tests-21%20passing-brightgreen)

Sistema web completo de gestión de Recursos Humanos con API REST, autenticación JWT y control de acceso por roles. Desarrollado con Python (FastAPI) + JavaScript + PostgreSQL.

> 🔗 **Demo en vivo:** https://sistema-rrhh-frontend.onrender.com
> 📄 **Documentación de la API:** https://sistema-de-gestion-de-rr-hh.onrender.com/docs
> 👤 **Usuario demo:** admin@empresa.com / Admin12345

> ⚠️ El backend usa el plan gratuito de Render — puede tardar 30-60 segundos en responder la primera vez (cold start). Después funciona con normalidad.

---

## 🎯 ¿Qué hace este sistema?

Permite a una empresa gestionar su personal de forma digital:
- Registrar empleados, departamentos y cargos
- Controlar asistencia diaria (entrada/salida con cálculo automático de horas y tardanza)
- Gestionar solicitudes de vacaciones con flujo de aprobación y cálculo de feriados peruanos
- Control de acceso según el rol del usuario (5 roles diferentes)
- Todo desplegado en producción y ejecutable localmente con Docker

---

## ✨ Características principales

- **API REST completa** con 30+ endpoints documentados automáticamente (Swagger/OpenAPI)
- **Autenticación JWT** con tokens Bearer
- **5 roles de usuario** con permisos diferenciados: ADMIN, RRHH, JEFE, EMPLEADO, CONSULTOR
- **Control de acceso por scope**: un JEFE solo ve su propio equipo; un EMPLEADO solo ve sus propios datos; un CONSULTOR no ve salario ni documento
- **Cálculo automático** de horas trabajadas, horas extras y estado de tardanza (límite: 8:15 AM)
- **Flujo de aprobación** de vacaciones con descuento/devolución automática de días disponibles
- **Feriados nacionales del Perú 2026**: 17 feriados registrados, con cálculo de días contiguos (si el día después de tus vacaciones es feriado, se descuenta automáticamente)
- **Registro manual de asistencia** para correcciones (RRHH/ADMIN)
- **Soft delete**: empleados y departamentos nunca se eliminan, solo se desactivan
- **21 tests automatizados** con pytest cubriendo auth, empleados y vacaciones
- **Dockerizado**: corre el sistema completo con un solo comando

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL 15 + SQLAlchemy ORM |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| Validación | Pydantic v2 |
| Servidor | Uvicorn |
| Frontend | HTML + CSS + JavaScript vanilla |
| Tests | pytest + httpx |
| DevOps | Docker + Docker Compose |
| Deploy | Render (Web Service + Static Site + PostgreSQL) |

---

## 📊 Modelo de datos

7 tablas relacionadas:

```
usuarios ──── empleados ──── departamentos
                  │               │
               asistencias    (jefe_id)
                  │
              vacaciones ──── feriados
                  │
               cargos
```

---

## 🚀 Instalación local con Docker

### Requisitos
- Docker Desktop instalado y corriendo

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Nameless4I/Sistema-de-gestion-de-RR.HH.git
cd Sistema-de-gestion-de-RR.HH

# 2. Levantar el sistema completo (backend + PostgreSQL)
docker-compose up --build

# 3. En otra terminal, crear el usuario admin y cargar feriados
docker-compose exec backend python -m app.seed
docker-compose exec backend python -m app.seed_feriados

# 4. Acceder a la documentación de la API
# http://localhost:8000/docs

```

---

## 🔧 Instalación local sin Docker

### Requisitos
- Python 3.10+
- PostgreSQL 14+
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Nameless4I/Sistema-de-gestion-de-RR.HH.git
cd Sistema-de-gestion-de-RR.HH

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus datos de PostgreSQL y una SECRET_KEY segura

# 5. Crear la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE rrhh_db;"

# 6. Levantar el servidor (crea las tablas automáticamente)
uvicorn app.main:app --reload

# 7. Crear el usuario ADMIN inicial y cargar feriados
python -m app.seed
python -m app.seed_feriados
```

---

## 👤 Usuario inicial

| Email | Password | Rol |
|---|---|---|
| admin@empresa.com | Admin12345 | ADMIN |

> ⚠️ Cambia la contraseña del admin en producción.

---

## 🧪 Correr los tests

```bash
# Crear la base de datos de test
psql -U postgres -c "CREATE DATABASE rrhh_test;"

# Correr los 21 tests
pytest tests/ -v
```

Los tests cubren:
- **Auth**: login exitoso, credenciales incorrectas, permisos de registro, token
- **Empleados**: crear, listar, obtener, permisos por rol, cese, documento duplicado
- **Vacaciones**: solicitar, feriados en rango, feriados contiguos, días insuficientes, solapamiento, aprobar, permisos

---

## 📋 Módulos y endpoints

### 🔐 Auth
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/auth/register | Crear usuario | ADMIN, RRHH |
| POST | /api/auth/login | Iniciar sesión | Público |
| GET | /api/auth/me | Perfil actual | Autenticado |

### 🏗️ Departamentos
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/departamentos | Listar | Autenticado |
| GET | /api/departamentos/{id} | Obtener | Autenticado |
| POST | /api/departamentos | Crear | ADMIN |
| PUT | /api/departamentos/{id} | Editar | ADMIN |
| DELETE | /api/departamentos/{id} | Desactivar | ADMIN |

### 💼 Cargos
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/cargos | Listar | Autenticado |
| GET | /api/cargos/{id} | Obtener | Autenticado |
| POST | /api/cargos | Crear | ADMIN |
| PUT | /api/cargos/{id} | Editar | ADMIN |

### 👥 Empleados
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/empleados | Listar | ADMIN, RRHH, JEFE*, CONSULTOR** |
| GET | /api/empleados/{id} | Obtener | ADMIN, RRHH, JEFE*, EMPLEADO*** |
| POST | /api/empleados | Crear | ADMIN, RRHH |
| PUT | /api/empleados/{id} | Editar completo | ADMIN, RRHH |
| PATCH | /api/empleados/{id}/contacto | Editar contacto propio | EMPLEADO |
| PATCH | /api/empleados/{id}/cese | Cesar empleado | ADMIN, RRHH |

> *JEFE: solo su departamento | **CONSULTOR: sin salario ni documento | ***EMPLEADO: solo su propio registro

### ⏰ Asistencias
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/asistencias/marcar-entrada | Marcar entrada | EMPLEADO |
| PATCH | /api/asistencias/marcar-salida | Marcar salida | EMPLEADO |
| POST | /api/asistencias/manual | Crear manual | ADMIN, RRHH |
| GET | /api/asistencias | Listar | Autenticado* |
| GET | /api/asistencias/{id} | Obtener | Autenticado* |
| PATCH | /api/asistencias/{id}/justificar | Justificar | ADMIN, RRHH |

### 🌴 Vacaciones
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| POST | /api/vacaciones | Solicitar | EMPLEADO |
| GET | /api/vacaciones | Listar | Autenticado* |
| GET | /api/vacaciones/{id} | Obtener | Autenticado* |
| PATCH | /api/vacaciones/{id}/aprobar | Aprobar | ADMIN, RRHH, JEFE |
| PATCH | /api/vacaciones/{id}/rechazar | Rechazar | ADMIN, RRHH, JEFE |
| PATCH | /api/vacaciones/{id}/cancelar | Cancelar | EMPLEADO |

### 📅 Feriados
| Método | Ruta | Descripción | Roles |
|---|---|---|---|
| GET | /api/feriados | Listar feriados 2026 | Autenticado |

---

## 🔑 Roles y permisos

| Rol | Descripción |
|---|---|
| ADMIN | Control total del sistema |
| RRHH | Gestión de personal, asistencia y aprobación de vacaciones |
| JEFE | Supervisor de su departamento (scope limitado) |
| EMPLEADO | Acceso solo a sus propios datos |
| CONSULTOR | Solo lectura, sin datos sensibles (salario, documento) |

---

## 📅 Feriados nacionales del Perú 2026

El sistema incluye los 17 feriados nacionales del Perú 2026 y aplica la siguiente regla de negocio:

> Si el día inmediatamente después del fin de tus vacaciones es feriado nacional, ese feriado se descuenta automáticamente de tus días disponibles (días contiguos).

**Ejemplo:** Solicitas vacaciones del lunes 27 al lunes 27 de julio. El martes 28 es feriado (Independencia) y el miércoles 29 también. El sistema descuenta **3 días** automáticamente (27 + 28 + 29).

---

## 📝 Notas técnicas

- Se fijó `bcrypt==4.0.1` por incompatibilidad conocida entre `passlib` y versiones más recientes de bcrypt (4.1+)
- `Base.metadata.create_all()` crea las tablas automáticamente al iniciar el servidor
- Para modificaciones de esquema en producción se recomienda implementar migraciones con **Alembic** (roadmap)
- Los seeds no corren durante los tests (variable de entorno `TESTING=true`)
- El email corporativo de un empleado cesado se libera automáticamente para poder reasignarlo

---

## 🗺️ Roadmap

- [ ] Módulo de Nómina (cálculo mensual, bonos, descuentos)
- [ ] Módulo de Evaluaciones de Desempeño
- [ ] Módulo de Capacitaciones
- [ ] Historial laboral de empleados
- [ ] Notificaciones por email al aprobar/rechazar vacaciones
- [ ] Migraciones con Alembic
- [ ] Feriados para años futuros (2027, 2028...)
- [ ] CI/CD con GitHub Actions

---

## 👨‍💻 Autor

**Jose Aldair Coronado Nalvarte**


[![GitHub](https://img.shields.io/badge/GitHub-Nameless4I-181717?logo=github)](https://github.com/Nameless4I)