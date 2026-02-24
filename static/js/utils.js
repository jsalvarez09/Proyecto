function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId)
  if (!el) return
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`
  setTimeout(() => el.innerHTML = '', 4000)
}

function openModal(id) {
  document.getElementById(id).classList.add('open')
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open')
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/static/login.html'
  }
}

function requireRole(...roles) {
  const user = getUser()
  if (!user || !roles.includes(user.role)) {
    return false
  }
  return true
}

function renderNavbar(container) {
  const user = getUser()
  container.innerHTML = `
    <nav class="navbar">
      <div class="navbar-brand">
        <span>🎓</span> Motor de Recomendación Docente
      </div>
      <div class="navbar-links">
        <span style="color:rgba(255,255,255,0.7);font-size:0.85rem">${user?.full_name} · ${user?.role}</span>
        <a href="#" onclick="logout()">Cerrar sesión</a>
      </div>
    </nav>
  `
}

function renderSidebar(container, active) {
  const user = getUser()
  const isAdmin = user?.role === 'ADMIN'
  const isEstudiante = user?.role === 'ESTUDIANTE'

  if (isEstudiante) {
    container.innerHTML = `
      <aside class="sidebar">
        <ul class="sidebar-menu">
          <li><a href="dashboard.html" class="${active === 'dashboard' ? 'active' : ''}"><span>📊</span> Dashboard</a></li>
          <li><a href="mis-materias.html" class="${active === 'mis-materias' ? 'active' : ''}"><span>📚</span> Mis Materias</a></li>
          <li><a href="mis-notas.html" class="${active === 'mis-notas' ? 'active' : ''}"><span>📋</span> Mis Notas</a></li>
        </ul>
      </aside>
    `
    return
  }

  container.innerHTML = `
    <aside class="sidebar">
      <ul class="sidebar-menu">
        <li><a href="dashboard.html" class="${active === 'dashboard' ? 'active' : ''}"><span>📊</span> Dashboard</a></li>
        <li><a href="students.html" class="${active === 'students' ? 'active' : ''}"><span>👨‍🎓</span> Estudiantes</a></li>
        <li><a href="teachers.html" class="${active === 'teachers' ? 'active' : ''}"><span>👨‍🏫</span> Profesores</a></li>
        <li><a href="subjects.html" class="${active === 'subjects' ? 'active' : ''}"><span>📚</span> Materias</a></li>
        <li><a href="grades.html" class="${active === 'grades' ? 'active' : ''}"><span>📝</span> Notas</a></li>
        ${isAdmin ? `<li><a href="users.html" class="${active === 'users' ? 'active' : ''}"><span>👥</span> Usuarios</a></li>` : ''}
      </ul>
    </aside>
  `
}

function logout() {
  clearSession()
  window.location.href = '/static/index.html'
}

function scoreToPercent(score) {
  return (score * 100).toFixed(1) + '%'
}