# ==== ETAPA 1: BUILD DEL FRONTEND ====
FROM node:20-alpine AS build

WORKDIR /app

# Configurar npm para evitar timeouts
RUN npm config set fetch-timeout 600000 && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias con caché y configuración de timeout extendida
RUN npm ci --legacy-peer-deps --prefer-offline --no-audit || \
    npm install --legacy-peer-deps --prefer-offline --no-audit

# Copiar el resto de archivos
COPY . .

# Construir Angular para producción
RUN npm run build -- --configuration production

# ==== ETAPA 2: SERVIDOR NGINX PARA PRODUCCIÓN ====
FROM nginx:alpine

# Copiar el build generado (ajustar ruta según tu proyecto)
COPY --from=build /app/dist/sena-frontend /usr/share/nginx/html

# Copiar la config de nginx para que soporte rutas (SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]