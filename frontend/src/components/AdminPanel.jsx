import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

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

// Calcula cuántas respuestas de un usuario ya tienen evaluación guardada
function countEvaluated(userResponses) {
  return userResponses.filter(r => r.evaluation || r.score).length
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
          <button className="btn-save" onClick={handleSave} disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar'}
          </button>
          {saved && <span className="save-ok">✓ Guardado</span>}
          {error && <span className="save-error">✗ {error}</span>}
        </div>
      </div>
    </div>
  )
}

// ── Acordeón de un usuario ────────────────────────────────────────────────────
function UserAccordion({ userId, userResponses, adminPwd, isOpen, onToggle }) {
  const evaluated = countEvaluated(userResponses)
  const total     = userResponses.length
  const allDone   = evaluated === total

  return (
    <div className={`user-accordion ${isOpen ? 'user-accordion--open' : ''}`}>
      <button className="user-accordion__header" onClick={onToggle}>
        <div className="user-accordion__info">
          <span className="user-accordion__name">{userResponses[0].user_name}</span>
          <span className="user-accordion__id">#{userId}</span>
        </div>
        <div className="user-accordion__meta">
          <span className={`user-accordion__badge ${allDone ? 'user-accordion__badge--done' : ''}`}>
            {evaluated}/{total} evaluadas
          </span>
          <span className="user-accordion__arrow">▼</span>
        </div>
      </button>

      {isOpen && (
        <div className="user-accordion__body">
          {userResponses.map(r => (
            <ResponseRow key={r.id} response={r} adminPwd={adminPwd} />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Panel de administración ───────────────────────────────────────────────────
export default function AdminPanel() {
  const { state }  = useLocation()
  const navigate   = useNavigate()
  const adminPwd   = state?.adminPwd ?? ''

  const [responses, setResponses]           = useState([])
  const [loading, setLoading]               = useState(true)
  const [error, setError]                   = useState(null)
  const [expandedUserId, setExpandedUserId] = useState(null)
  const [changePwdMsg, setChangePwdMsg]     = useState(null)
  const [changePwdError, setChangePwdError] = useState(null)

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
        setError(err.response?.data?.detail ?? err.message)
        setLoading(false)
      })
  }, [adminPwd])

  function toggleUser(userId) {
    // Clic en el mismo usuario abierto → cierra. Clic en otro → abre ese.
    setExpandedUserId(prev => prev === userId ? null : userId)
  }

  async function handleChangePassword() {
    const newPwd = window.prompt('Nueva contraseña de administrador:')
    if (newPwd === null) return
    if (!newPwd.trim()) { setChangePwdError('La contraseña no puede estar vacía.'); return }
    setChangePwdMsg(null); setChangePwdError(null)
    try {
      await axios.patch(
        `${API_URL}/admin/change-password/`,
        { new_password: newPwd },
        { headers: { 'X-Admin-Password': adminPwd } },
      )
      setChangePwdMsg('✓ Contraseña actualizada. Se resetea al reiniciar el contenedor.')
      setTimeout(() => setChangePwdMsg(null), 6000)
    } catch (err) {
      setChangePwdError('✗ ' + (err.response?.data?.detail ?? err.message))
    }
  }

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
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button className="btn-back" onClick={handleChangePassword}>🔑 Cambiar contraseña</button>
          <button className="btn-back" onClick={() => navigate('/')}>← Volver al formulario</button>
        </div>
      </div>

      {changePwdMsg   && <p className="save-ok"   style={{ marginBottom: '0.75rem' }}>{changePwdMsg}</p>}
      {changePwdError && <p className="save-error" style={{ marginBottom: '0.75rem' }}>{changePwdError}</p>}

      <p className="page__subtitle">
        {byUser.size} encuestado(s) · {responses.length} respuestas en total.
        Hacé clic en un nombre para ver el detalle.
      </p>

      {byUser.size === 0 && (
        <p className="status-msg">Aún no hay respuestas enviadas.</p>
      )}

      {Array.from(byUser.entries()).map(([userId, userResponses]) => (
        <UserAccordion
          key={userId}
          userId={userId}
          userResponses={userResponses}
          adminPwd={adminPwd}
          isOpen={expandedUserId === userId}
          onToggle={() => toggleUser(userId)}
        />
      ))}
    </div>
  )
}
