FROM node:20-slim AS builder

LABEL org.opencontainers.image.source=https://github.com/ssciwr/sample_flow
LABEL org.opencontainers.image.description="SampleFlow frontend production image"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build-only

FROM nginx

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
