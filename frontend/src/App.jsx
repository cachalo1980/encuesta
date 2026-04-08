import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import SectionAccordion from './components/SectionAccordion'

const API_URL = 'http://localhost:8001'

// Transforma el array plano de preguntas en un array de secciones ordenadas.
// Devuelve: [{ name: "1. Perfil General", questions: [...] }, ...]
// Usamos un array (no un objeto) para preservar el orden de inserción.
function buildSections(questions) {
  const map = new Map()
  for (const q of questions) {
    if (!map.has(q.section)) map.set(q.section, [])
    map.get(q.section).push(q)
  }
  return Array.from(map.entries()).map(([name, questions]) => ({ name, questions }))
}

export default function App() {
  const [sections, setSections] = useState([])   // array de { name, questions }
  const [answers, setAnswers]   = useState({})   // { [question_id]: valor }
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/questions/`)
      .then(res => {
        setSections(buildSections(res.data))
        setLoading(false)
      })
      .catch(err => {
        setError(`Error al cargar el cuestionario: ${err.message}`)
        setLoading(false)
      })
  }, [])

  // Actualiza el estado global de respuestas.
  // Se pasa hacia abajo como prop para que los acordeones puedan escribir en él.
  function handleChange(questionId, value) {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  function handleSubmit() {
    console.log('Respuestas acumuladas:', answers)
    alert('Respuestas registradas en consola (F12 → Console).\nEl envío al backend llega en el próximo sprint.')
  }

  if (loading) return <p className="status-msg">Cargando cuestionario...</p>
  if (error)   return <p className="status-msg status-msg--error">{error}</p>

  return (
    <div className="page">
      <h1 className="page__title">DevMentor — Cuestionario de Diagnóstico</h1>
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
            initialOpen={index === 0}   // la primera sección arranca abierta
          />
        ))}

        <div className="submit-area">
          <button type="button" className="btn-submit" onClick={handleSubmit}>
            Enviar Cuestionario
          </button>
        </div>
      </form>
    </div>
  )
}
