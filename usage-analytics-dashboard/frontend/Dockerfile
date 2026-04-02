FROM node:20-alpine
WORKDIR /app
COPY frontend/package.json frontend/tsconfig.json frontend/vite.config.ts frontend/index.html ./
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm install
EXPOSE 5173
CMD ["npm", "run", "dev"]
