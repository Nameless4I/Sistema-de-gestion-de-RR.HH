// ============================================
// CONFIGURACIÓN DE LA API
// ============================================

// Cambia esta URL a la de Render cuando hagas deploy
const API_BASE = 'http://127.0.0.1:8000';

// ============================================
// MANEJO DE SESIÓN
// ============================================

const session = {
  getToken: () => localStorage.getItem('token'),
  getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
  setSession: (token, user) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  isLoggedIn: () => !!localStorage.getItem('token'),
};

// ============================================
// CLIENTE HTTP
// ============================================

async function apiFetch(endpoint, options = {}) {
  const token = session.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    session.clear();
    window.location.href = '/index.html';
    return;
  }

  const data = response.status !== 204 ? await response.json() : null;

  if (!response.ok) {
    const message = data?.detail || 'Error en la solicitud';
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }

  return data;
}

// Helpers para los métodos HTTP
const api = {
  get: (endpoint) => apiFetch(endpoint),
  post: (endpoint, body) => apiFetch(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint, body) => apiFetch(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (endpoint, body = {}) => apiFetch(endpoint, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' }),
};

// ============================================
// HELPERS DE UI
// ============================================

function showAlert(elementId, message, type = 'error') {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.className = `alert alert-${type} show`;
  el.textContent = message;
  setTimeout(() => el.classList.remove('show'), 5000);
}

function badgeEstado(estado) {
  const map = {
    'ACTIVO': 'green', 'APROBADO': 'green', 'PRESENTE': 'green',
    'CESADO': 'red', 'RECHAZADO': 'red', 'AUSENTE': 'red',
    'PENDIENTE': 'orange', 'TARDANZA': 'orange', 'SUSPENDIDO': 'orange',
    'JUSTIFICADO': 'blue', 'CANCELADO': 'gray', 'GOZADO': 'gray',
  };
  const color = map[estado] || 'gray';
  return `<span class="badge badge-${color}">${estado}</span>`;
}

function formatFecha(fechaStr) {
  if (!fechaStr) return '—';
  return new Date(fechaStr).toLocaleDateString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  });
}

function formatHora(horaStr) {
  if (!horaStr) return '—';
  return horaStr.substring(0, 5);
}

function getUserInitials(email) {
  return email ? email.substring(0, 2).toUpperCase() : '??';
}

function checkAuth() {
  if (!session.isLoggedIn()) {
    window.location.href = '/index.html';
  }
}

function logout() {
  session.clear();
  window.location.href = '/index.html';
}