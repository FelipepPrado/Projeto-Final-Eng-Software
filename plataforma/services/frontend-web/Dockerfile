FROM node:20-alpine AS build
WORKDIR /app

ARG VITE_AUTH_API
ARG VITE_ASSIGN_API
ARG VITE_ACADEMIC_API

ENV VITE_AUTH_API=$VITE_AUTH_API
ENV VITE_ASSIGN_API=$VITE_ASSIGN_API
ENV VITE_ACADEMIC_API=$VITE_ACADEMIC_API

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]