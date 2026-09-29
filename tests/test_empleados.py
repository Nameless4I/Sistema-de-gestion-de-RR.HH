def test_crear_empleado(client, admin_token, departamento, cargo):
    response = client.post("/api/empleados",
        json={
            "nombre": "María",
            "apellido_paterno": "López",
            "tipo_documento": "DNI",
            "numero_documento": "87654321",
            "fecha_contrato": "2026-01-01",
            "tipo_contrato": "INDEFINIDO",
            "salario": 3500,
            "dias_vacaciones_disponibles": 30,
            "departamento_id": departamento.id,
            "cargo_id": cargo.id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "María"
    assert response.json()["estado"] == "ACTIVO"


def test_listar_empleados(client, admin_token, empleado):
    response = client.get("/api/empleados",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_empleado(client, admin_token, empleado):
    response = client.get(f"/api/empleados/{empleado.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == empleado.id


def test_empleado_no_puede_ver_otro(client, empleado_token, empleado, db):
    from app.models.empleado import Empleado
    from datetime import date
    otro = Empleado(
        nombre="Otro", apellido_paterno="Empleado",
        tipo_documento="DNI", numero_documento="99999999",
        fecha_contrato=date(2026, 1, 1), tipo_contrato="INDEFINIDO",
        salario=2000, dias_vacaciones_disponibles=30, estado="ACTIVO"
    )
    db.add(otro)
    db.commit()

    response = client.get(f"/api/empleados/{otro.id}",
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 403


def test_cesar_empleado(client, admin_token, empleado):
    response = client.patch(f"/api/empleados/{empleado.id}/cese",
        json={"fecha_cese": "2026-09-01", "motivo": "Renuncia voluntaria"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "CESADO"


def test_documento_duplicado(client, admin_token, empleado):
    response = client.post("/api/empleados",
        json={
            "nombre": "Otro",
            "apellido_paterno": "Persona",
            "tipo_documento": "DNI",
            "numero_documento": "12345678",  # mismo DNI que el fixture
            "fecha_contrato": "2026-01-01",
            "tipo_contrato": "INDEFINIDO",
            "salario": 2000,
            "dias_vacaciones_disponibles": 30
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400