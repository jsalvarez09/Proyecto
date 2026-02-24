const API = 'http://localhost:8000/api/v1'

function getToken() {
  return localStorage.getItem('token')
}

function getUser() {
  const u = localStorage.getItem('user')
  return u ? JSON.parse(u) : null
}

function setSession(token, user) {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
}

function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

async function request(method, endpoint, body = null) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const config = { method, headers }
  if (body) config.body = JSON.stringify(body)

  const res = await fetch(`${API}${endpoint}`, config)

  if (res.status === 401) {
    clearSession()
    window.location.href = '/static/login.html'
    return
  }

  if (res.status === 204) return null

  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error en la solicitud')
  return data
}

const api = {
  // Auth
  login: (email, password) => request('POST', '/auth/login', { email, password }),
  me: () => request('GET', '/auth/me'),

  // Estudiantes
  getStudents: (search = '') => request('GET', `/students${search ? '?search=' + search : ''}`),
  createStudent: (data) => request('POST', '/students', data),
  updateStudent: (id, data) => request('PUT', `/students/${id}`, data),
  deleteStudent: (id) => request('DELETE', `/students/${id}`),

  // Profesores
  getTeachers: () => request('GET', '/teachers'),
  createTeacher: (data) => request('POST', '/teachers', data),
  updateTeacher: (id, data) => request('PUT', `/teachers/${id}`, data),
  deleteTeacher: (id) => request('DELETE', `/teachers/${id}`),

  // Materias
  getSubjects: () => request('GET', '/subjects'),
  createSubject: (data) => request('POST', '/subjects', data),
  updateSubject: (id, data) => request('PUT', `/subjects/${id}`, data),
  deleteSubject: (id) => request('DELETE', `/subjects/${id}`),
  getSubject: (id) => request('GET', `/subjects/${id}`),
  enrollStudents: (id, student_ids) => request('POST', `/subjects/${id}/enrollments`, { student_ids }),
  removeEnrollment: (subjectId, studentId) => request('DELETE', `/subjects/${subjectId}/enrollments/${studentId}`),
  getGroupProfile: (id) => request('GET', `/subjects/${id}/group-profile`),

  // Recomendaciones
  recommend: (subjectId) => request('POST', `/subjects/${subjectId}/recommend`),
  getRecommendations: (subjectId) => request('GET', `/subjects/${subjectId}/recommendations`),

  // Usuarios
  getUsers: () => request('GET', '/users'),
  createUser: (data) => request('POST', '/users', data),
  updateUser: (id, data) => request('PUT', `/users/${id}`, data),
}