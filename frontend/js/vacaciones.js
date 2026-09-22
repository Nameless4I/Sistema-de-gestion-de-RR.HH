// ============================================
// VACACIONES
// ============================================

checkAuth();

const user = session.getUser();
document.getElementById('userAvatar').textContent = getUserInitials(user?.email);
document.getElementById('userName').textContent = user?.email?.split('@')[0] || '—';
document.getElementById('userRole').textContent = user?.rol || '—';

if (user?.rol !== 'ADMIN') {
  document.getElementById('adminSection').style.display = 'none';
  document.getElementById('navDepartamentos').style.display = 'none';
  document.getElementById('navCargos').style.display = 'none';
}

// Mostrar botón solicitar solo para EMPLEADO
if (user?.rol === 'EMPLEADO') {
  document.getElementById('btnSolicitar').style.display = 'inline-flex';
  document.getElementById('cardDias').style.display = 'block';
}

let vacaciones = [];
let decisionId = null;
let decisionTipo = null;
let diasDisponibles = 0;

// ============================================
// CARGAR DATOS
// ============================================

async function cargarVacaciones() {
  try {
    vacaciones = await api.get('/api/vacaciones');
    renderTabla(vacaciones);
    document.getElementById('totalVacaciones').textContent = `Solicitudes (${vacaciones.length})`;
  } catch (error) {
    console.error('Error cargando vacaciones:', error);
  }
}

async function cargarDiasDisponibles() {
  if (user?.rol !== 'EMPLEADO') return;
  try {
    const me = await api.get('/api/auth/me');
    if (me.empleado) {
      const emp = await api.get(`/api/empleados/${me.empleado.id}`);
      diasDisponibles = emp.dias_vacaciones_disponibles;
      document.getElementById('diasDisponibles').textContent = diasDisponibles;
      document.getElementById('diasModal').textContent = diasDisponibles;
    }
  } catch (error) {
    console.error('Error cargando días:', error);
  }
}

// ============================================
// RENDER TABLA
// ============================================

function renderTabla(lista) {
  const tbody = document.getElementById('tablaVacaciones');
  const puedeDecision = ['ADMIN', 'RRHH', 'JEFE'].includes(user?.rol);
  const esEmpleado = user?.rol === 'EMPLEADO';

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">🌴</div><p>No hay solicitudes de vacaciones</p></div></td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(v => `
    <tr>
      <td>Empleado #${v.empleado_id}</td>
      <td>${formatFecha(v.fecha_inicio)}</td>
      <td>${formatFecha(v.fecha_fin)}</td>
      <td style="text-align:center; font-weight:600;">${v.dias_tomados}</td>
      <td>${v.tipo}</td>
      <td>${badgeEstado(v.estado)}</td>
      <td>
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
          ${puedeDecision && v.estado === 'PENDIENTE' ? `
            <button class="btn btn-success btn-sm" onclick="abrirModalDecision(${v.id}, 'aprobar')">✓ Aprobar</button>
            <button class="btn btn-danger btn-sm" onclick="abrirModalDecision(${v.id}, 'rechazar')">✕ Rechazar</button>
          ` : ''}
          ${esEmpleado && ['PENDIENTE', 'APROBADO'].includes(v.estado) ? `
            <button class="btn btn-secondary btn-sm" onclick="cancelarVacacion(${v.id})">Cancelar</button>
          ` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

// ============================================
// FILTROS
// ============================================

document.getElementById('filtroEstado').addEventListener('change', () => {
  const estado = document.getElementById('filtroEstado').value;
  const filtrados = estado ? vacaciones.filter(v => v.estado === estado) : vacaciones;
  renderTabla(filtrados);
});

// ============================================
// MODAL SOLICITAR
// ============================================

function abrirModalSolicitar() {
  document.getElementById('vacFechaInicio').value = '';
  document.getElementById('vacFechaFin').value = '';
  document.getElementById('vacObservaciones').value = '';
  document.getElementById('diasCalculados').style.display = 'none';
  document.getElementById('modalSolicitar').classList.add('show');
}

function cerrarModalSolicitar() {
  document.getElementById('modalSolicitar').classList.remove('show');
}

// Calcular días al cambiar fechas
['vacFechaInicio', 'vacFechaFin'].forEach(id => {
  document.getElementById(id).addEventListener('change', calcularDias);
});

function calcularDias() {
  const inicio = document.getElementById('vacFechaInicio').value;
  const fin = document.getElementById('vacFechaFin').value;

  if (inicio && fin && fin >= inicio) {
    const dias = Math.floor((new Date(fin) - new Date(inicio)) / (1000 * 60 * 60 * 24)) + 1;
    document.getElementById('diasCount').textContent = dias;
    document.getElementById('diasCalculados').style.display = 'block';

    // Advertencia si supera los días disponibles
    const container = document.getElementById('diasCalculados');
    if (dias > diasDisponibles) {
      container.style.background = 'var(--red-bg)';
      container.style.color = 'var(--red)';
      document.getElementById('diasCount').textContent = `${dias} ⚠️ supera tus días disponibles`;
    } else {
      container.style.background = 'var(--gray-bg)';
      container.style.color = 'var(--text)';
    }
  } else {
    document.getElementById('diasCalculados').style.display = 'none';
  }
}

async function confirmarSolicitar() {
  const inicio = document.getElementById('vacFechaInicio').value;
  const fin = document.getElementById('vacFechaFin').value;

  if (!inicio || !fin) {
    showAlert('alertSolicitar', 'Selecciona las fechas de inicio y fin');
    return;
  }

  if (fin < inicio) {
    showAlert('alertSolicitar', 'La fecha fin no puede ser anterior a la fecha inicio');
    return;
  }

  try {
    await api.post('/api/vacaciones', {
      fecha_inicio: inicio,
      fecha_fin: fin,
      tipo: document.getElementById('vacTipo').value,
      observaciones: document.getElementById('vacObservaciones').value.trim() || null
    });
    cerrarModalSolicitar();
    await cargarVacaciones();
    await cargarDiasDisponibles();
  } catch (error) {
    showAlert('alertSolicitar', error.message);
  }
}

// ============================================
// MODAL DECISION (aprobar / rechazar)
// ============================================

function abrirModalDecision(id, tipo) {
  decisionId = id;
  decisionTipo = tipo;

  const esAprobar = tipo === 'aprobar';
  document.getElementById('modalDecisionTitle').textContent = esAprobar ? '✓ Aprobar solicitud' : '✕ Rechazar solicitud';
  document.getElementById('modalDecisionDesc').textContent = esAprobar
    ? 'Al aprobar, los días se descontarán automáticamente del saldo del empleado.'
    : 'Al rechazar, no se descontarán días del saldo del empleado.';

  const btn = document.getElementById('btnConfirmarDecision');
  btn.className = `btn btn-sm ${esAprobar ? 'btn-success' : 'btn-danger'}`;
  btn.style.width = 'auto';
  btn.textContent = esAprobar ? 'Confirmar aprobación' : 'Confirmar rechazo';

  document.getElementById('decisionObservaciones').value = '';
  document.getElementById('modalDecision').classList.add('show');
}

function cerrarModalDecision() {
  document.getElementById('modalDecision').classList.remove('show');
}

async function confirmarDecision() {
  try {
    await api.patch(`/api/vacaciones/${decisionId}/${decisionTipo}`, {
      observaciones: document.getElementById('decisionObservaciones').value.trim() || null
    });
    cerrarModalDecision();
    await cargarVacaciones();
  } catch (error) {
    showAlert('alertDecision', error.message);
  }
}

// ============================================
// CANCELAR (EMPLEADO)
// ============================================

async function cancelarVacacion(id) {
  if (!confirm('¿Estás seguro de que quieres cancelar esta solicitud?')) return;
  try {
    await api.patch(`/api/vacaciones/${id}/cancelar`, {});
    await cargarVacaciones();
    await cargarDiasDisponibles();
  } catch (error) {
    alert(error.message);
  }
}

// ============================================
// INICIALIZAR
// ============================================

cargarVacaciones();
cargarDiasDisponibles();