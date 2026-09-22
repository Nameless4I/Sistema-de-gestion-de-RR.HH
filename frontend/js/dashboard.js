// ============================================
// DASHBOARD
// ============================================

checkAuth();

const user = session.getUser();

// Mostrar info del usuario en sidebar
document.getElementById('userAvatar').textContent = getUserInitials(user?.email);
document.getElementById('userName').textContent = user?.email?.split('@')[0] || '—';
document.getElementById('userRole').textContent = user?.rol || '—';
document.getElementById('welcomeMsg').textContent = `Bienvenido, ${user?.email?.split('@')[0]}`;

// Mostrar fecha de hoy
const hoy = new Date();
document.getElementById('fechaHoy').textContent = hoy.toLocaleDateString('es-PE', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Ocultar sección admin si no es ADMIN
if (user?.rol !== 'ADMIN') {
  document.getElementById('adminSection').style.display = 'none';
  document.getElementById('navDepartamentos').style.display = 'none';
  document.getElementById('navCargos').style.display = 'none';
}

// ============================================
// CARGAR ESTADÍSTICAS
// ============================================

async function cargarStats() {
  try {
    const [empleados, asistencias, vacaciones, departamentos] = await Promise.all([
      api.get('/api/empleados'),
      api.get('/api/asistencias'),
      api.get('/api/vacaciones'),
      api.get('/api/departamentos'),
    ]);

    // Total empleados activos
    const activos = empleados.filter(e => e.estado === 'ACTIVO').length;
    document.getElementById('statEmpleados').textContent = activos;

    // Asistencias de hoy
    const fechaHoy = new Date().toISOString().split('T')[0];
    const asistenciasHoy = asistencias.filter(a => a.fecha === fechaHoy);
    document.getElementById('statAsistencias').textContent = asistenciasHoy.length;

    // Vacaciones pendientes
    const pendientes = vacaciones.filter(v => v.estado === 'PENDIENTE').length;
    document.getElementById('statVacaciones').textContent = pendientes;

    // Departamentos activos
    const deptActivos = departamentos.filter(d => d.activo).length;
    document.getElementById('statDepartamentos').textContent = deptActivos;

    // Tabla asistencias recientes (últimas 5 de hoy)
    const tablaAsis = document.getElementById('tablaAsistencias');
    if (asistenciasHoy.length === 0) {
      tablaAsis.innerHTML = `<tr><td colspan="3"><div class="empty-state"><div class="empty-icon">⏰</div><p>Sin asistencias hoy</p></div></td></tr>`;
    } else {
      tablaAsis.innerHTML = asistenciasHoy.slice(0, 5).map(a => `
        <tr>
          <td>Empleado #${a.empleado_id}</td>
          <td>${formatHora(a.hora_entrada)}</td>
          <td>${badgeEstado(a.estado)}</td>
        </tr>
      `).join('');
    }

    // Tabla vacaciones recientes (últimas 5)
    const tablaVac = document.getElementById('tablaVacaciones');
    const recentesVac = vacaciones.slice(-5).reverse();
    if (recentesVac.length === 0) {
      tablaVac.innerHTML = `<tr><td colspan="3"><div class="empty-state"><div class="empty-icon">🌴</div><p>Sin solicitudes</p></div></td></tr>`;
    } else {
      tablaVac.innerHTML = recentesVac.map(v => `
        <tr>
          <td>#${v.empleado_id}</td>
          <td style="font-size:12px;">${formatFecha(v.fecha_inicio)} → ${formatFecha(v.fecha_fin)}</td>
          <td>${badgeEstado(v.estado)}</td>
        </tr>
      `).join('');
    }

  } catch (error) {
    console.error('Error cargando stats:', error);
  }
}

cargarStats();