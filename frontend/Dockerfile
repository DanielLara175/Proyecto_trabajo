# ==== ETAPA 1: BUILD DEL FRONTEND ====
FROM node:20 AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# 🟢 Construye Angular para producción
RUN npm run build --prod


# ==== ETAPA 2: SERVIDOR NGINX PARA PRODUCCIÓN ====
FROM nginx:alpine

# 🟢 Copia el build generado
COPY --from=build /app/dist/sena-frontend /usr/share/nginx/html

# 🟢 Copia la config de nginx para que soporte rutas (SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
