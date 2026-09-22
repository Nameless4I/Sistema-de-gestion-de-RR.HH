// ============================================
// CARGOS
// ============================================

checkAuth();

const user = session.getUser();
document.getElementById('userAvatar').textContent = getUserInitials(user?.email);
document.getElementById('userName').textContent = user?.email?.split('@')[0] || '—';
document.getElementById('userRole').textContent = user?.rol || '—';

if (user?.rol !== 'ADMIN') {
  window.location.href = 'dashboard.html';
}

let cargos = [];
let editandoId = null;

const nivelLabels = {
  JUNIOR: 'Junior', SEMI_SENIOR: 'Semi Senior',
  SENIOR: 'Senior', LEAD: 'Lead', GERENTE: 'Gerente'
};

const nivelColores = {
  JUNIOR: 'gray', SEMI_SENIOR: 'blue',
  SENIOR: 'green', LEAD: 'orange', GERENTE: 'red'
};

async function cargarCargos() {
  try {
    cargos = await api.get('/api/cargos');
    renderTabla(cargos);
    document.getElementById('totalCargos').textContent = `Cargos (${cargos.length})`;
  } catch (error) {
    console.error('Error:', error);
  }
}

function renderTabla(lista) {
  const tbody = document.getElementById('tablaCargos');
  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">💼</div><p>No hay cargos registrados</p></div></td></tr>`;
    return;
  }
  tbody.innerHTML = lista.map(c => `
    <tr>
      <td style="font-weight:500;">${c.nombre}</td>
      <td><span class="badge badge-${nivelColores[c.nivel] || 'gray'}">${nivelLabels[c.nivel] || c.nivel}</span></td>
      <td>${c.salario_base ? `S/. ${parseFloat(c.salario_base).toLocaleString('es-PE', {minimumFractionDigits:2})}` : '—'}</td>
      <td style="color:var(--gray-text);">${c.descripcion || '—'}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="editar(${c.id})">Editar</button>
      </td>
    </tr>
  `).join('');
}

document.getElementById('searchInput').addEventListener('input', (e) => {
  const texto = e.target.value.toLowerCase();
  renderTabla(cargos.filter(c => c.nombre.toLowerCase().includes(texto)));
});

function abrirModal() {
  editandoId = null;
  document.getElementById('modalTitle').textContent = 'Nuevo cargo';
  document.getElementById('cargoNombre').value = '';
  document.getElementById('cargoNivel').value = 'JUNIOR';
  document.getElementById('cargoSalario').value = '';
  document.getElementById('cargoDescripcion').value = '';
  document.getElementById('modalCargo').classList.add('show');
}

function cerrarModal() {
  document.getElementById('modalCargo').classList.remove('show');
}

function editar(id) {
  const cargo = cargos.find(c => c.id === id);
  if (!cargo) return;
  editandoId = id;
  document.getElementById('modalTitle').textContent = 'Editar cargo';
  document.getElementById('cargoNombre').value = cargo.nombre;
  document.getElementById('cargoNivel').value = cargo.nivel;
  document.getElementById('cargoSalario').value = cargo.salario_base || '';
  document.getElementById('cargoDescripcion').value = cargo.descripcion || '';
  document.getElementById('modalCargo').classList.add('show');
}

async function guardar() {
  const nombre = document.getElementById('cargoNombre').value.trim();
  if (!nombre) {
    showAlert('alertModal', 'El nombre es obligatorio');
    return;
  }

  const datos = {
    nombre,
    nivel: document.getElementById('cargoNivel').value,
    salario_base: document.getElementById('cargoSalario').value ? parseFloat(document.getElementById('cargoSalario').value) : null,
    descripcion: document.getElementById('cargoDescripcion').value.trim() || null,
  };

  try {
    if (editandoId) {
      await api.put(`/api/cargos/${editandoId}`, datos);
    } else {
      await api.post('/api/cargos', datos);
    }
    cerrarModal();
    await cargarCargos();
  } catch (error) {
    showAlert('alertModal', error.message);
  }
}

cargarCargos();