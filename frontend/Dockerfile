FROM node:16-slim

WORKDIR /app

COPY . .

RUN npm install -g http-server

RUN npm install

RUN npm run build-only

# debug server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "80"]

# production server
# CMD ["http-server", "dist"]
