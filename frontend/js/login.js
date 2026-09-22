// ============================================
// LOGIN
// ============================================

// Si ya está logueado, redirigir al dashboard
if (session.isLoggedIn()) {
  window.location.href = 'pages/dashboard.html';
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const btn = document.getElementById('submitBtn');

  btn.disabled = true;
  btn.textContent = 'Ingresando...';

  try {
    const data = await api.post('/api/auth/login', { email, password });

    // Guardar token y datos del usuario
    session.setSession(data.access_token, data.usuario);

    // Redirigir al dashboard
    window.location.href = 'pages/dashboard.html';

  } catch (error) {
    showAlert('alert', error.message || 'Credenciales incorrectas');
    btn.disabled = false;
    btn.textContent = 'Iniciar sesión';
  }
});