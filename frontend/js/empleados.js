// ============================================
// EMPLEADOS
// ============================================

checkAuth();

const user = session.getUser();
document.getElementById('userAvatar').textContent = getUserInitials(user?.email);
document.getElementById('userName').textContent = user?.email?.split('@')[0] || '—';
document.getElementById('userRole').textContent = user?.rol || '—';

// Ocultar sección admin si no es ADMIN
if (user?.rol !== 'ADMIN') {
  document.getElementById('adminSection').style.display = 'none';
  document.getElementById('navDepartamentos').style.display = 'none';
  document.getElementById('navCargos').style.display = 'none';
}

// Ocultar botón crear si no tiene permisos
if (!['ADMIN', 'RRHH'].includes(user?.rol)) {
  document.getElementById('btnNuevoEmpleado').style.display = 'none';
}

let empleados = [];
let empleadoEditandoId = null;
let empleadoCeseId = null;

// ============================================
// CARGAR DATOS
// ============================================

async function cargarEmpleados() {
  try {
    empleados = await api.get('/api/empleados');
    renderTabla(empleados);
    document.getElementById('totalEmpleados').textContent = `Empleados (${empleados.length})`;
  } catch (error) {
    console.error('Error cargando empleados:', error);
  }
}

async function cargarSelectores() {
  try {
    const [departamentos, cargos] = await Promise.all([
      api.get('/api/departamentos'),
      api.get('/api/cargos'),
    ]);

    const selectDept = document.getElementById('empDepartamento');
    departamentos.filter(d => d.activo).forEach(d => {
      selectDept.innerHTML += `<option value="${d.id}">${d.nombre}</option>`;
    });

    const selectCargo = document.getElementById('empCargo');
    cargos.forEach(c => {
      selectCargo.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
    });
  } catch (error) {
    console.error('Error cargando selectores:', error);
  }
}

// ============================================
// RENDER TABLA
// ============================================

function renderTabla(lista) {
  const tbody = document.getElementById('tablaEmpleados');

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">👥</div><p>No se encontraron empleados</p></div></td></tr>`;
    return;
  }

  const puedeEditar = ['ADMIN', 'RRHH'].includes(user?.rol);

  tbody.innerHTML = lista.map(e => `
    <tr>
      <td>
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:32px; height:32px; border-radius:50%; background:var(--blue); color:white; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:600; flex-shrink:0;">
            ${e.nombre[0]}${e.apellido_paterno[0]}
          </div>
          <div>
            <div style="font-weight:500;">${e.nombre} ${e.apellido_paterno}</div>
            <div style="color:var(--gray-text); font-size:12px;">${e.email_corporativo || '—'}</div>
          </div>
        </div>
      </td>
      <td>${e.tipo_documento}: ${e.numero_documento}</td>
      <td>${e.cargo_id ? `#${e.cargo_id}` : '—'}</td>
      <td>${e.tipo_contrato}</td>
      <td style="text-align:center;">
        <span style="font-weight:600; color:var(--blue);">${e.dias_vacaciones_disponibles}</span>
      </td>
      <td>${badgeEstado(e.estado)}</td>
      <td>
        <div style="display:flex; gap:6px;">
          ${puedeEditar ? `
            <button class="btn btn-secondary btn-sm" onclick="editarEmpleado(${e.id})">Editar</button>
            ${e.estado === 'ACTIVO' ? `<button class="btn btn-danger btn-sm" onclick="abrirModalCese(${e.id})">Cesar</button>` : ''}
          ` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

// ============================================
// BÚSQUEDA Y FILTROS
// ============================================

document.getElementById('searchInput').addEventListener('input', filtrar);
document.getElementById('filtroEstado').addEventListener('change', filtrar);

function filtrar() {
  const texto = document.getElementById('searchInput').value.toLowerCase();
  const estado = document.getElementById('filtroEstado').value;

  const filtrados = empleados.filter(e => {
    const matchTexto = !texto ||
      `${e.nombre} ${e.apellido_paterno} ${e.numero_documento}`.toLowerCase().includes(texto);
    const matchEstado = !estado || e.estado === estado;
    return matchTexto && matchEstado;
  });

  renderTabla(filtrados);
}

// ============================================
// MODAL CREAR / EDITAR
// ============================================

document.getElementById('btnNuevoEmpleado').onclick = () => {
  empleadoEditandoId = null;
  document.getElementById('modalTitle').textContent = 'Nuevo empleado';
  limpiarForm();
  document.getElementById('modalEmpleado').classList.add('show');
};

function cerrarModal() {
  document.getElementById('modalEmpleado').classList.remove('show');
}

function limpiarForm() {
  ['empNombre','empApellidoP','empApellidoM','empNumDoc','empFechaNac',
   'empTelefono','empEmailP','empEmailC','empDireccion','empSalario','empFechaContrato']
    .forEach(id => document.getElementById(id).value = '');
  document.getElementById('empTipoDoc').value = 'DNI';
  document.getElementById('empTipoContrato').value = 'INDEFINIDO';
  document.getElementById('empDiasVac').value = '30';
  document.getElementById('empDepartamento').value = '';
  document.getElementById('empCargo').value = '';
}

function editarEmpleado(id) {
  const emp = empleados.find(e => e.id === id);
  if (!emp) return;

  empleadoEditandoId = id;
  document.getElementById('modalTitle').textContent = 'Editar empleado';

  document.getElementById('empNombre').value = emp.nombre || '';
  document.getElementById('empApellidoP').value = emp.apellido_paterno || '';
  document.getElementById('empApellidoM').value = emp.apellido_materno || '';
  document.getElementById('empTipoDoc').value = emp.tipo_documento || 'DNI';
  document.getElementById('empNumDoc').value = emp.numero_documento || '';
  document.getElementById('empFechaNac').value = emp.fecha_nacimiento || '';
  document.getElementById('empTelefono').value = emp.telefono || '';
  document.getElementById('empEmailP').value = emp.email_personal || '';
  document.getElementById('empEmailC').value = emp.email_corporativo || '';
  document.getElementById('empDireccion').value = emp.direccion || '';
  document.getElementById('empSalario').value = emp.salario || '';
  document.getElementById('empFechaContrato').value = emp.fecha_contrato || '';
  document.getElementById('empTipoContrato').value = emp.tipo_contrato || 'INDEFINIDO';
  document.getElementById('empDiasVac').value = emp.dias_vacaciones_disponibles || 30;
  document.getElementById('empDepartamento').value = emp.departamento_id || '';
  document.getElementById('empCargo').value = emp.cargo_id || '';

  document.getElementById('modalEmpleado').classList.add('show');
}

async function guardarEmpleado() {
  const btn = document.getElementById('btnGuardar');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  const datos = {
    nombre: document.getElementById('empNombre').value.trim(),
    apellido_paterno: document.getElementById('empApellidoP').value.trim(),
    apellido_materno: document.getElementById('empApellidoM').value.trim() || null,
    tipo_documento: document.getElementById('empTipoDoc').value,
    numero_documento: document.getElementById('empNumDoc').value.trim(),
    fecha_nacimiento: document.getElementById('empFechaNac').value || null,
    telefono: document.getElementById('empTelefono').value.trim() || null,
    email_personal: document.getElementById('empEmailP').value.trim() || null,
    email_corporativo: document.getElementById('empEmailC').value.trim() || null,
    direccion: document.getElementById('empDireccion').value.trim() || null,
    salario: parseFloat(document.getElementById('empSalario').value),
    fecha_contrato: document.getElementById('empFechaContrato').value,
    tipo_contrato: document.getElementById('empTipoContrato').value,
    dias_vacaciones_disponibles: parseInt(document.getElementById('empDiasVac').value),
    departamento_id: document.getElementById('empDepartamento').value ? parseInt(document.getElementById('empDepartamento').value) : null,
    cargo_id: document.getElementById('empCargo').value ? parseInt(document.getElementById('empCargo').value) : null,
  };

  try {
    if (empleadoEditandoId) {
      await api.put(`/api/empleados/${empleadoEditandoId}`, datos);
    } else {
      await api.post('/api/empleados', datos);
    }
    cerrarModal();
    await cargarEmpleados();
  } catch (error) {
    showAlert('alertModal', error.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Guardar';
  }
}

// ============================================
// MODAL CESE
// ============================================

function abrirModalCese(id) {
  empleadoCeseId = id;
  document.getElementById('ceseFecha').value = new Date().toISOString().split('T')[0];
  document.getElementById('cesMotivo').value = '';
  document.getElementById('modalCese').classList.add('show');
}

function cerrarModalCese() {
  document.getElementById('modalCese').classList.remove('show');
}

async function confirmarCese() {
  const fecha = document.getElementById('ceseFecha').value;
  const motivo = document.getElementById('cesMotivo').value.trim();

  if (!fecha || !motivo) {
    showAlert('alertCese', 'Completa todos los campos');
    return;
  }

  try {
    await api.patch(`/api/empleados/${empleadoCeseId}/cese`, {
      fecha_cese: fecha,
      motivo: motivo
    });
    cerrarModalCese();
    await cargarEmpleados();
  } catch (error) {
    showAlert('alertCese', error.message);
  }
}

// ============================================
// INICIALIZAR
// ============================================

cargarEmpleados();
cargarSelectores();