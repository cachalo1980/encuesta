FROM node:20-alpine

WORKDIR /app

# Copia solo el manifiesto primero para aprovechar la caché de capas de Docker.
# Si package.json no cambia, Docker reutiliza la capa de npm install
# en builds posteriores, acelerando enormemente el proceso.
COPY package*.json ./
RUN npm install

# El código fuente se copia aquí, pero en dev será sobreescrito
# por el bind-mount del docker-compose (./frontend:/app).
COPY . .

EXPOSE 4000

# --host  → escucha en 0.0.0.0 (accesible fuera del contenedor)
# --port  → usa el puerto 4000 en lugar del 5173 por defecto de Vite,
#           evitando conflictos con otros contenedores en WSL (5173 y 3000 ocupados)
CMD ["npm", "run", "dev", "--", "--host", "--port", "4000"]
