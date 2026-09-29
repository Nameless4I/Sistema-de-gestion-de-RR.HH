def test_login_exitoso(client, admin_user):
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin12345"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["usuario"]["rol"] == "ADMIN"


def test_login_credenciales_incorrectas(client, admin_user):
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_usuario_inexistente(client):
    response = client.post("/api/auth/login", json={
        "email": "noexiste@test.com",
        "password": "cualquier"
    })
    assert response.status_code == 401


def test_me_autenticado(client, admin_token):
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"


def test_me_sin_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]  # HTTPBearer devuelve 403


def test_register_exitoso(client, admin_token, empleado):
    response = client.post("/api/auth/register",
        json={
            "email": "nuevo@test.com",
            "password": "Nuevo12345",
            "empleado_id": empleado.id,
            "rol": "EMPLEADO"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "nuevo@test.com"


def test_register_sin_permiso(client, empleado_token, empleado):
    response = client.post("/api/auth/register",
        json={
            "email": "otro@test.com",
            "password": "Otro12345",
            "empleado_id": empleado.id,
            "rol": "EMPLEADO"
        },
        headers={"Authorization": f"Bearer {empleado_token}"}
    )
    assert response.status_code == 403


def test_register_password_corta(client, admin_token, empleado):
    response = client.post("/api/auth/register",
        json={
            "email": "corta@test.com",
            "password": "123",
            "empleado_id": empleado.id,
            "rol": "EMPLEADO"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422