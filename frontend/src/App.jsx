import { useState, useEffect } from 'react'
import axios from 'axios'

// El frontend corre en http://localhost:3000 (host → contenedor 5173).
// El backend corre en http://localhost:8001 (host → contenedor 8000).
// El navegador hace la petición directamente a localhost:8001,
// que es el puerto del HOST. Docker expone ese puerto al host,
// por eso funciona. El CORS configurado en Sprint 4 le indica
// al navegador que este origen (localhost:3000) está permitido.
const API_URL = 'http://localhost:8001'

function App() {
  const [backendStatus, setBackendStatus] = useState('Conectando...')
  const [error, setError] = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/health`)
      .then(res => {
        setBackendStatus(JSON.stringify(res.data))
        setError(null)
      })
      .catch(err => {
        setError(`Error: ${err.message}`)
        setBackendStatus('—')
      })
  }, [])

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>DevMentor Survey</h1>
      <hr />
      <h2>Conexión con el backend</h2>
      {error
        ? <p style={{ color: 'red' }}>{error}</p>
        : <p>Estado: <strong>{backendStatus}</strong></p>
      }
    </div>
  )
}

export default App
