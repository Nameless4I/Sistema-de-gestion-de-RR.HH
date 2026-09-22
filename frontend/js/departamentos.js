// ============================================
// DEPARTAMENTOS
// ============================================

checkAuth();

const user = session.getUser();
document.getElementById('userAvatar').textContent = getUserInitials(user?.email);
document.getElementById('userName').textContent = user?.email?.split('@')[0] || '—';
document.getElementById('userRole').textContent = user?.rol || '—';

// Solo ADMIN puede acceder
if (user?.rol !== 'ADMIN') {
  window.location.href = 'dashboard.html';
}

let departamentos = [];
let editandoId = null;

async function cargarDepartamentos() {
  try {
    departamentos = await api.get('/api/departamentos');
    renderTabla(departamentos);
    document.getElementById('totalDepts').textContent = `Departamentos (${departamentos.length})`;
  } catch (error) {
    console.error('Error:', error);
  }
}

function renderTabla(lista) {
  const tbody = document.getElementById('tablaDepts');
  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">🏗️</div><p>No hay departamentos</p></div></td></tr>`;
    return;
  }
  tbody.innerHTML = lista.map(d => `
    <tr>
      <td style="font-weight:500;">${d.nombre}</td>
      <td style="color:var(--gray-text);">${d.descripcion || '—'}</td>
      <td>${d.jefe_id ? `#${d.jefe_id}` : '—'}</td>
      <td>${d.activo ? '<span class="badge badge-green">Activo</span>' : '<span class="badge badge-gray">Inactivo</span>'}</td>
      <td>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-secondary btn-sm" onclick="editar(${d.id})">Editar</button>
          ${d.activo ? `<button class="btn btn-danger btn-sm" onclick="desactivar(${d.id})">Desactivar</button>` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

document.getElementById('searchInput').addEventListener('input', (e) => {
  const texto = e.target.value.toLowerCase();
  const filtrados = departamentos.filter(d => d.nombre.toLowerCase().includes(texto));
  renderTabla(filtrados);
});

function abrirModal() {
  editandoId = null;
  document.getElementById('modalTitle').textContent = 'Nuevo departamento';
  document.getElementById('deptNombre').value = '';
  document.getElementById('deptDescripcion').value = '';
  document.getElementById('deptJefeId').value = '';
  document.getElementById('modalDept').classList.add('show');
}

function cerrarModal() {
  document.getElementById('modalDept').classList.remove('show');
}

function editar(id) {
  const dept = departamentos.find(d => d.id === id);
  if (!dept) return;
  editandoId = id;
  document.getElementById('modalTitle').textContent = 'Editar departamento';
  document.getElementById('deptNombre').value = dept.nombre;
  document.getElementById('deptDescripcion').value = dept.descripcion || '';
  document.getElementById('deptJefeId').value = dept.jefe_id || '';
  document.getElementById('modalDept').classList.add('show');
}

async function guardar() {
  const datos = {
    nombre: document.getElementById('deptNombre').value.trim(),
    descripcion: document.getElementById('deptDescripcion').value.trim() || null,
    jefe_id: document.getElementById('deptJefeId').value ? parseInt(document.getElementById('deptJefeId').value) : null,
  };

  if (!datos.nombre) {
    showAlert('alertModal', 'El nombre es obligatorio');
    return;
  }

  try {
    if (editandoId) {
      await api.put(`/api/departamentos/${editandoId}`, datos);
    } else {
      await api.post('/api/departamentos', datos);
    }
    cerrarModal();
    await cargarDepartamentos();
  } catch (error) {
    showAlert('alertModal', error.message);
  }
}

async function desactivar(id) {
  if (!confirm('¿Desactivar este departamento?')) return;
  try {
    await api.delete(`/api/departamentos/${id}`);
    await cargarDepartamentos();
  } catch (error) {
    alert(error.message);
  }
}

cargarDepartamentos();