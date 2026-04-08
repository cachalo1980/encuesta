import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 4000,
    // Dominio público permitido para el servidor de desarrollo de Vite.
    // Vite 5+ bloquea por defecto peticiones de hosts no reconocidos
    // (protección contra ataques DNS rebinding).
    allowedHosts: ['encuesta.caruao.cloud'],
  },
})
