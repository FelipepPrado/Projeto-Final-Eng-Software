FROM node:20-alpine AS build
WORKDIR /app

# Declarar os build args (Render injeta automaticamente os valores das env vars com esses nomes)
ARG VITE_AUTH_API
ARG VITE_ASSIGN_API

# Expor como ENV para o Vite conseguir ler via import.meta.env durante o build
ENV VITE_AUTH_API=$VITE_AUTH_API
ENV VITE_ASSIGN_API=$VITE_ASSIGN_API

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]