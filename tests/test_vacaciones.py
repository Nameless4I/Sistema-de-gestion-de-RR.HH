from datetime import date

def test_solicitar_vacaciones(client, empleado_token, empleado_user):
    response = client.post("/api/vacaciones",
        json={
            "fecha_inicio": "2026-10-01",
            "fecha_fin": "2026-10-05",
            "tipo": "ANUAL"
        },
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 201
    assert response.json()["dias_tomados"] == 5
    assert response.json()["estado"] == "PENDIENTE"


def test_vacaciones_con_feriado_en_rango(client, empleado_token, empleado_user, feriado_independencia):
    # 27 al 29 julio — el 28 es feriado (dentro del rango)
    response = client.post("/api/vacaciones",
        json={
            "fecha_inicio": "2026-07-27",
            "fecha_fin": "2026-07-29",
            "tipo": "ANUAL"
        },
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 201
    assert response.json()["dias_tomados"] == 3  # 27, 28 (feriado), 29


def test_vacaciones_con_feriado_contiguo(client, empleado_token, empleado_user, feriado_independencia):
    # Solo el 27 — el 28 es feriado contiguo, se suma
    response = client.post("/api/vacaciones",
        json={
            "fecha_inicio": "2026-07-27",
            "fecha_fin": "2026-07-27",
            "tipo": "ANUAL"
        },
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 201
    assert response.json()["dias_tomados"] == 2  # 27 + 28 feriado contiguo


def test_vacaciones_sin_dias_suficientes(client, empleado_token, empleado_user):
    # 35 días cuando solo tiene 30
    response = client.post("/api/vacaciones",
        json={
            "fecha_inicio": "2026-10-01",
            "fecha_fin": "2026-11-04",  # 35 días
            "tipo": "ANUAL"
        },
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 400
    assert "días disponibles" in response.json()["detail"]


def test_solapamiento_vacaciones(client, empleado_token, empleado_user):
    # Primera solicitud
    client.post("/api/vacaciones",
        json={"fecha_inicio": "2026-10-01", "fecha_fin": "2026-10-05", "tipo": "ANUAL"},
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    # Segunda solicitud que se solapa
    response = client.post("/api/vacaciones",
        json={"fecha_inicio": "2026-10-03", "fecha_fin": "2026-10-08", "tipo": "ANUAL"},
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 400
    assert "solapa" in response.json()["detail"]


def test_aprobar_vacaciones(client, admin_token, empleado_token, empleado_user):
    # Crear solicitud
    sol = client.post("/api/vacaciones",
        json={"fecha_inicio": "2026-10-01", "fecha_fin": "2026-10-03", "tipo": "ANUAL"},
        headers={"Authorization": f"Bearer {empleado_token}"}
    ).json()

    # Aprobar como admin
    response = client.patch(f"/api/vacaciones/{sol['id']}/aprobar",
        json={"observaciones": "Aprobado"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "APROBADO"


def test_empleado_no_puede_aprobar(client, empleado_token, empleado_user):
    sol = client.post("/api/vacaciones",
        json={"fecha_inicio": "2026-10-01", "fecha_fin": "2026-10-03", "tipo": "ANUAL"},
        headers={"Authorization": f"Bearer {empleado_token}"}
    ).json()

    response = client.patch(f"/api/vacaciones/{sol['id']}/aprobar",
        json={},
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 403