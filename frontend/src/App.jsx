import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import axios from 'axios'
import './App.css'
import SectionAccordion from './components/SectionAccordion'
import AdminPanel from './components/AdminPanel'

const API_URL = 'http://localhost:8001'

function buildSections(questions) {
  const map = new Map()
  for (const q of questions) {
    if (!map.has(q.section)) map.set(q.section, [])
    map.get(q.section).push(q)
  }
  return Array.from(map.entries()).map(([name, questions]) => ({ name, questions }))
}

function buildPayload(answers) {
  return Object.entries(answers)
    .filter(([, v]) => v !== undefined && v !== '' && v !== null)
    .map(([questionId, value]) => ({
      question_id:  Number(questionId),
      text_answer:  typeof value === 'string' ? value : null,
      scale_answer: typeof value === 'number' ? value : null,
    }))
}

// ── Barra de navegación ───────────────────────────────────────────────────────
function Navbar({ onAdminClick }) {
  const navigate = useNavigate()
  return (
    <nav className="navbar">
      <span className="navbar__brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
        <span className="brand-prompt">&gt;_</span> DevMentor
      </span>
      <button className="btn-admin" onClick={onAdminClick}>
        Admin
      </button>
    </nav>
  )
}

// ── Formulario de registro ────────────────────────────────────────────────────
function RegistrationForm({ onRegistered }) {
  const [name, setName]       = useState('')
  const [email, setEmail]     = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim() || !email.trim()) {
      setError('Por favor, completá todos los campos.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post(`${API_URL}/users/`, { name: name.trim(), email: email.trim() })
      onRegistered(res.data.id, res.data.name)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1 className="page__title">Cuestionario de Diagnóstico</h1>
      <p className="page__subtitle">
        Antes de empezar, ingresá tus datos. Si ya lo completaste antes, usá el mismo email
        para retomar donde lo dejaste.
      </p>
      <form className="registration-form" onSubmit={handleSubmit}>
        <div className="reg-field">
          <label className="reg-label" htmlFor="reg-name">Nombre completo</label>
          <input
            id="reg-name"
            className="q-input-text"
            type="text"
            placeholder="Ej: Juan García"
            value={name}
            onChange={e => setName(e.target.value)}
            autoFocus
          />
        </div>
        <div className="reg-field">
          <label className="reg-label" htmlFor="reg-email">Email</label>
          <input
            id="reg-email"
            className="q-input-text"
            type="email"
            placeholder="Ej: juan@example.com"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>
        {error && <p className="status-msg status-msg--error" style={{ padding: '0.5rem 0' }}>✗ {error}</p>}
        <div className="submit-area" style={{ marginTop: '1.5rem' }}>
          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? 'Iniciando...' : 'Comenzar cuestionario →'}
          </button>
        </div>
      </form>
    </div>
  )
}

// ── Formulario del cuestionario ───────────────────────────────────────────────
function SurveyPage() {
  const [userId, setUserId]           = useState(null)
  const [userName, setUserName]       = useState('')
  const [sections, setSections]       = useState([])
  const [answers, setAnswers]         = useState({})
  const [loading, setLoading]         = useState(true)
  const [loadError, setLoadError]     = useState(null)
  const [submitting, setSubmitting]   = useState(false)
  const [submitOk, setSubmitOk]       = useState(false)
  const [submitError, setSubmitError] = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/questions/`)
      .then(res => { setSections(buildSections(res.data)); setLoading(false) })
      .catch(err => { setLoadError(`Error al cargar el cuestionario: ${err.message}`); setLoading(false) })
  }, [])

  function handleRegistered(id, name) {
    setUserId(id)
    setUserName(name)
  }

  function handleChange(questionId, value) {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
    setSubmitOk(false)
    setSubmitError(null)
  }

  async function handleSubmit() {
    const payload = buildPayload(answers)
    if (payload.length === 0) { setSubmitError('No has respondido ninguna pregunta todavía.'); return }

    setSubmitting(true); setSubmitOk(false); setSubmitError(null)
    try {
      await axios.post(`${API_URL}/users/${userId}/responses/`, payload)
      setSubmitOk(true)
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    } catch (err) {
      setSubmitError(`Error al enviar: ${err.response?.data?.detail ?? err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading)   return <p className="status-msg">Cargando cuestionario...</p>
  if (loadError) return <p className="status-msg status-msg--error">{loadError}</p>

  // Mostrar registro si todavía no tenemos el ID del usuario
  if (!userId) {
    return <RegistrationForm onRegistered={handleRegistered} />
  }

  const totalAnswered = Object.values(answers).filter(v => v !== undefined && v !== '' && v !== null).length

  return (
    <div className="page">
      <h1 className="page__title">Cuestionario de Diagnóstico</h1>
      <p className="page__subtitle">
        Hola, <strong>{userName}</strong>. Responde con honestidad — no hay respuestas correctas
        ni incorrectas. Hacé clic en cada sección para desplegarla.
      </p>

      <form onSubmit={e => e.preventDefault()}>
        {sections.map((section, index) => (
          <SectionAccordion
            key={section.name}
            sectionName={section.name}
            questions={section.questions}
            answers={answers}
            onChange={handleChange}
            initialOpen={index === 0}
          />
        ))}

        <div className="submit-area">
          <p className="submit-progress">{totalAnswered} de 61 preguntas respondidas</p>
          <button type="button" className="btn-submit" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Enviando...' : 'Enviar Cuestionario'}
          </button>
          {submitOk    && <div className="submit-feedback submit-feedback--ok">✓ Respuestas guardadas correctamente. ¡Gracias!</div>}
          {submitError && <div className="submit-feedback submit-feedback--error">✗ {submitError}</div>}
        </div>
      </form>
    </div>
  )
}

// ── App raíz: routing + navbar ────────────────────────────────────────────────
export default function App() {
  const navigate = useNavigate()

  function handleAdminClick() {
    const pwd = window.prompt('Contraseña de administrador:')
    if (pwd === null) return
    navigate('/admin', { state: { adminPwd: pwd } })
  }

  return (
    <>
      <Navbar onAdminClick={handleAdminClick} />
      <Routes>
        <Route path="/"      element={<SurveyPage />} />
        <Route path="/admin" element={<AdminPanel  />} />
        <Route path="*"      element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
