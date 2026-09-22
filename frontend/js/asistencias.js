// ============================================
// ASISTENCIAS
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

let asistencias = [];
let asistenciaJustificarId = null;

// Mostrar botones según rol
if (user?.rol === 'EMPLEADO') {
  document.getElementById('cardHoy').style.display = 'block';
  document.getElementById('btnEntrada').style.display = 'inline-flex';
  document.getElementById('btnSalida').style.display = 'inline-flex';
}

if (['ADMIN', 'RRHH'].includes(user?.rol)) {
  document.getElementById('btnManual').style.display = 'inline-flex';
  document.getElementById('colAcciones').style.display = '';
}

// ============================================
// CARGAR ASISTENCIAS
// ============================================

async function cargarAsistencias() {
  try {
    asistencias = await api.get('/api/asistencias');
    renderTabla(asistencias);
    document.getElementById('totalAsistencias').textContent = `Asistencias (${asistencias.length})`;

    // Si es EMPLEADO, mostrar estado de hoy
    if (user?.rol === 'EMPLEADO') {
      actualizarCardHoy();
    }
  } catch (error) {
    console.error('Error cargando asistencias:', error);
  }
}

function actualizarCardHoy() {
  const hoy = new Date().toISOString().split('T')[0];
  const asistenciaHoy = asistencias.find(a => a.fecha === hoy);

  const estadoEl = document.getElementById('estadoHoy');
  const horasEl = document.getElementById('horasTrabajadas');
  const btnEntrada = document.getElementById('btnEntrada');
  const btnSalida = document.getElementById('btnSalida');

  if (!asistenciaHoy) {
    estadoEl.textContent = 'Aún no has marcado tu entrada hoy';
    horasEl.textContent = '—';
    btnEntrada.style.display = 'inline-flex';
    btnSalida.style.display = 'none';
  } else if (!asistenciaHoy.hora_salida) {
    estadoEl.innerHTML = `Entrada registrada a las <strong>${formatHora(asistenciaHoy.hora_entrada)}</strong> · ${badgeEstado(asistenciaHoy.estado)}`;
    horasEl.textContent = '—';
    btnEntrada.style.display = 'none';
    btnSalida.style.display = 'inline-flex';
  } else {
    estadoEl.innerHTML = `Entrada: <strong>${formatHora(asistenciaHoy.hora_entrada)}</strong> · Salida: <strong>${formatHora(asistenciaHoy.hora_salida)}</strong> · ${badgeEstado(asistenciaHoy.estado)}`;
    horasEl.textContent = asistenciaHoy.horas_trabajadas || '—';
    btnEntrada.style.display = 'none';
    btnSalida.style.display = 'none';
  }
}

// ============================================
// RENDER TABLA
// ============================================

function renderTabla(lista) {
  const tbody = document.getElementById('tablaAsistencias');
  const puedeJustificar = ['ADMIN', 'RRHH'].includes(user?.rol);

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><div class="empty-icon">⏰</div><p>No hay registros de asistencia</p></div></td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(a => `
    <tr>
      <td>Empleado #${a.empleado_id}</td>
      <td>${formatFecha(a.fecha)}</td>
      <td>${formatHora(a.hora_entrada)}</td>
      <td>${formatHora(a.hora_salida)}</td>
      <td style="text-align:center; font-weight:600;">
        ${a.horas_trabajadas ? `${a.horas_trabajadas}h` : '—'}
        ${a.horas_extras > 0 ? `<span style="color:var(--orange); font-size:11px;"> +${a.horas_extras}h extra</span>` : ''}
      </td>
      <td>${a.tipo}</td>
      <td>${badgeEstado(a.estado)}</td>
      <td>
        ${puedeJustificar ? `
          <button class="btn btn-secondary btn-sm" onclick="abrirModalJustificar(${a.id})">Justificar</button>
        ` : ''}
      </td>
    </tr>
  `).join('');
}

// ============================================
// FILTROS
// ============================================

document.getElementById('filtroFecha').addEventListener('change', filtrar);
document.getElementById('filtroEstado').addEventListener('change', filtrar);

function filtrar() {
  const fecha = document.getElementById('filtroFecha').value;
  const estado = document.getElementById('filtroEstado').value;

  const filtrados = asistencias.filter(a => {
    const matchFecha = !fecha || a.fecha === fecha;
    const matchEstado = !estado || a.estado === estado;
    return matchFecha && matchEstado;
  });

  renderTabla(filtrados);
}

// ============================================
// MARCAR ENTRADA / SALIDA
// ============================================

async function marcarEntrada() {
  const btn = document.getElementById('btnEntrada');
  btn.disabled = true;
  btn.textContent = 'Marcando...';
  try {
    await api.post('/api/asistencias/marcar-entrada', {});
    await cargarAsistencias();
  } catch (error) {
    alert(error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🟢 Marcar entrada';
  }
}

async function marcarSalida() {
  const btn = document.getElementById('btnSalida');
  btn.disabled = true;
  btn.textContent = 'Marcando...';
  try {
    await api.patch('/api/asistencias/marcar-salida', {});
    await cargarAsistencias();
  } catch (error) {
    alert(error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🔴 Marcar salida';
  }
}

// ============================================
// MODAL JUSTIFICAR
// ============================================

function abrirModalJustificar(id) {
  asistenciaJustificarId = id;
  document.getElementById('justObservaciones').value = '';
  document.getElementById('modalJustificar').classList.add('show');
}

function cerrarModalJustificar() {
  document.getElementById('modalJustificar').classList.remove('show');
}

async function confirmarJustificar() {
  try {
    await api.patch(`/api/asistencias/${asistenciaJustificarId}/justificar`, {
      estado: document.getElementById('justEstado').value,
      observaciones: document.getElementById('justObservaciones').value.trim()
    });
    cerrarModalJustificar();
    await cargarAsistencias();
  } catch (error) {
    showAlert('alertJustificar', error.message);
  }
}

// ============================================
// MODAL MANUAL
// ============================================

function abrirModalManual() {
  document.getElementById('manFecha').value = new Date().toISOString().split('T')[0];
  document.getElementById('modalManual').classList.add('show');
}

function cerrarModalManual() {
  document.getElementById('modalManual').classList.remove('show');
}

async function confirmarManual() {
  try {
    await api.post('/api/asistencias/manual', {
      empleado_id: parseInt(document.getElementById('manEmpleadoId').value),
      fecha: document.getElementById('manFecha').value,
      hora_entrada: document.getElementById('manEntrada').value || null,
      hora_salida: document.getElementById('manSalida').value || null,
      tipo: document.getElementById('manTipo').value,
      observaciones: document.getElementById('manObservaciones').value.trim() || null
    });
    cerrarModalManual();
    await cargarAsistencias();
  } catch (error) {
    showAlert('alertManual', error.message);
  }
}

// ============================================
// INICIALIZAR
// ============================================

cargarAsistencias();