FROM node:16-slim as builder

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build-only

FROM nginx

COPY --from=builder dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
