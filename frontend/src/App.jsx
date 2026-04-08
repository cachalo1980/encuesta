import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import axios from 'axios'
import './App.css'
import SectionAccordion from './components/SectionAccordion'
import AdminPanel from './components/AdminPanel'

const API_URL = 'http://localhost:8001'
const USER_ID = 1  // Placeholder hasta Sprint 10 (registro/login)

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
        DevMentor Survey
      </span>
      <button className="btn-admin" onClick={onAdminClick}>
        Admin
      </button>
    </nav>
  )
}

// ── Formulario del cuestionario ───────────────────────────────────────────────
function SurveyPage() {
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
      await axios.post(`${API_URL}/users/${USER_ID}/responses/`, payload)
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

  const totalAnswered = Object.values(answers).filter(v => v !== undefined && v !== '' && v !== null).length

  return (
    <div className="page">
      <h1 className="page__title">Cuestionario de Diagnóstico</h1>
      <p className="page__subtitle">
        Responde con honestidad. No hay respuestas correctas ni incorrectas.
        Haz clic en cada sección para desplegarla.
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
    // window.prompt es síncrono y bloquea el hilo — aceptable para un acceso
    // interno y puntual. En producción se usaría un modal con formulario controlado.
    const pwd = window.prompt('Contraseña de administrador:')
    if (pwd === null) return  // el usuario canceló
    // Navegamos a /admin pasando la contraseña en el estado de la ruta.
    // useLocation().state en AdminPanel la recupera sin exponerla en la URL.
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
