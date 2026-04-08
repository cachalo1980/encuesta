import { useState } from 'react'

// ── QuestionInput ─────────────────────────────────────────────────────────────
// Renderiza el input correcto según question_type.
// Vive aquí porque está acoplado directamente al acordeón.
function QuestionInput({ question, value, onChange }) {
  const { id, question_type } = question

  if (question_type === 'TEXT') {
    return (
      <input
        type="text"
        className="q-input-text"
        value={value ?? ''}
        onChange={e => onChange(id, e.target.value)}
        placeholder="Tu respuesta"
      />
    )
  }

  if (question_type === 'PARAGRAPH') {
    return (
      <textarea
        className="q-textarea"
        value={value ?? ''}
        onChange={e => onChange(id, e.target.value)}
        rows={4}
        placeholder="Tu respuesta"
      />
    )
  }

  if (question_type === 'LINEAR_SCALE') {
    return (
      <div className="q-scale">
        <span className="scale-edge">1 — bajo</span>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => (
          <label key={n} className="scale-option">
            <input
              type="radio"
              name={`question_${id}`}
              value={n}
              checked={value === n}
              onChange={() => onChange(id, n)}
            />
            <span>{n}</span>
          </label>
        ))}
        <span className="scale-edge">10 — alto</span>
      </div>
    )
  }

  return null
}


// ── SectionAccordion ──────────────────────────────────────────────────────────
// Props:
//   sectionName  — string con el nombre de la sección (ej. "2. Desarrollo")
//   questions    — array de preguntas de esa sección
//   answers      — objeto global { [question_id]: valor } que vive en App.jsx
//   onChange     — función para actualizar answers en App.jsx
//   initialOpen  — boolean; true para la primera sección (mejora UX inicial)
export default function SectionAccordion({
  sectionName,
  questions,
  answers,
  onChange,
  initialOpen = false,
}) {
  // Estado local: solo este componente decide si está abierto o cerrado.
  // No necesita subir al estado global porque no afecta a otras secciones.
  const [isOpen, setIsOpen] = useState(initialOpen)

  // Calcula cuántas preguntas de esta sección ya tienen respuesta.
  // Sirve como indicador de progreso visible al usuario.
  const answered = questions.filter(q => {
    const v = answers[q.id]
    return v !== undefined && v !== '' && v !== null
  }).length

  const total = questions.length
  const allDone = answered === total

  return (
    <div className={`accordion ${isOpen ? 'accordion--open' : ''}`}>
      {/* ── Cabecera clicable ── */}
      <button
        type="button"
        className="accordion__header"
        onClick={() => setIsOpen(prev => !prev)}
        aria-expanded={isOpen}
      >
        <span className="accordion__title">{sectionName}</span>

        <span className="accordion__meta">
          <span className={`accordion__badge ${allDone ? 'accordion__badge--done' : ''}`}>
            {answered}/{total}
          </span>
          {/* La flecha rota con CSS cuando la sección está abierta */}
          <span className="accordion__arrow" aria-hidden="true">▼</span>
        </span>
      </button>

      {/* ── Cuerpo: visible solo cuando isOpen === true ── */}
      {isOpen && (
        <div className="accordion__body">
          {questions.map(q => (
            <div key={q.id} className="question-block">
              <label className="question-label">
                <span className="question-order">{q.order}.</span>
                {' '}{q.text}
                {q.is_required && <span className="question-required"> *</span>}
              </label>
              <QuestionInput
                question={q}
                value={answers[q.id]}
                onChange={onChange}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
