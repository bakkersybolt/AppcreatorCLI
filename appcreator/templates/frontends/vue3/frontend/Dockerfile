FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# The dev server port comes from FRONTEND_PORT (see docker-compose.yml)
CMD ["npm", "run", "dev", "--", "--host"]
