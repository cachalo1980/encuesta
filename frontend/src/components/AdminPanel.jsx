import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = 'http://localhost:8001'

// Agrupa el array plano de respuestas por user_id.
// Devuelve: Map { 1 => [...respuestas], 2 => [...respuestas] }
function groupByUser(responses) {
  const map = new Map()
  for (const r of responses) {
    if (!map.has(r.user_id)) map.set(r.user_id, [])
    map.get(r.user_id).push(r)
  }
  return map
}

// ── Fila de una respuesta individual ─────────────────────────────────────────
function ResponseRow({ response, adminPwd }) {
  const [evaluation, setEvaluation] = useState(response.evaluation ?? '')
  const [score, setScore]           = useState(response.score ?? '')
  const [saving, setSaving]         = useState(false)
  const [saved, setSaved]           = useState(false)
  const [error, setError]           = useState(null)

  async function handleSave() {
    setSaving(true); setSaved(false); setError(null)
    try {
      await axios.patch(
        `${API_URL}/admin/responses/${response.id}/`,
        {
          evaluation: evaluation || null,
          score: score !== '' ? Number(score) : null,
        },
        { headers: { 'X-Admin-Password': adminPwd } },
      )
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setSaving(false)
    }
  }

  // Muestra el valor de la respuesta según el tipo
  const answerDisplay = response.scale_answer !== null
    ? <span className="answer-scale">{response.scale_answer} / 10</span>
    : <span className="answer-text">{response.text_answer || <em>Sin respuesta</em>}</span>

  return (
    <div className="response-row">
      <p className="response-question">
        <span className="response-qid">#{response.question_id}</span> {response.question_text}
      </p>
      <div className="response-answer">{answerDisplay}</div>

      <div className="evaluation-form">
        <textarea
          className="evaluation-input"
          placeholder="Escribe tu evaluación aquí..."
          rows={2}
          value={evaluation}
          onChange={e => { setEvaluation(e.target.value); setSaved(false) }}
        />
        <div className="evaluation-score-row">
          <label className="score-label">
            Puntuación:
            <select
              className="score-select"
              value={score}
              onChange={e => { setScore(e.target.value); setSaved(false) }}
            >
              <option value="">—</option>
              {[1,2,3,4,5,6,7,8,9,10].map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <button
            className="btn-save"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Guardando...' : 'Guardar'}
          </button>
          {saved && <span className="save-ok">✓ Guardado</span>}
          {error && <span className="save-error">✗ {error}</span>}
        </div>
      </div>
    </div>
  )
}

// ── Panel de administración ───────────────────────────────────────────────────
export default function AdminPanel() {
  const { state }       = useLocation()
  const navigate        = useNavigate()
  const adminPwd        = state?.adminPwd ?? ''

  const [responses, setResponses] = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)

  useEffect(() => {
    if (!adminPwd) {
      setError('No se proporcionó contraseña. Vuelve al inicio.')
      setLoading(false)
      return
    }

    axios.get(`${API_URL}/admin/responses/`, {
      headers: { 'X-Admin-Password': adminPwd },
    })
      .then(res => { setResponses(res.data); setLoading(false) })
      .catch(err => {
        const detail = err.response?.data?.detail ?? err.message
        setError(detail)
        setLoading(false)
      })
  }, [adminPwd])

  if (loading) return <p className="status-msg">Cargando respuestas...</p>

  if (error) return (
    <div className="page">
      <p className="status-msg status-msg--error">✗ {error}</p>
      <div style={{ textAlign: 'center', marginTop: '1rem' }}>
        <button className="btn-back" onClick={() => navigate('/')}>← Volver</button>
      </div>
    </div>
  )

  const byUser = groupByUser(responses)

  return (
    <div className="page">
      <div className="admin-header">
        <h1 className="page__title">Panel de Administración</h1>
        <button className="btn-back" onClick={() => navigate('/')}>← Volver al formulario</button>
      </div>
      <p className="page__subtitle">
        {responses.length} respuestas de {byUser.size} usuario(s).
      </p>

      {responses.length === 0 && (
        <p className="status-msg">Aún no hay respuestas enviadas.</p>
      )}

      {Array.from(byUser.entries()).map(([userId, userResponses]) => (
        <section key={userId} className="user-section">
          <h2 className="user-section__title">Usuario #{userId}</h2>
          {userResponses.map(r => (
            <ResponseRow key={r.id} response={r} adminPwd={adminPwd} />
          ))}
        </section>
      ))}
    </div>
  )
}
