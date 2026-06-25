FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer cache: only re-run when package.json changes)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source — in dev, this is overridden by a volume mount in docker-compose
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
