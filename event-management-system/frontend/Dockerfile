FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json vite.config.ts index.html ./
COPY src ./src
RUN npm install
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
