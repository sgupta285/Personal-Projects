FROM node:20-alpine
WORKDIR /app
COPY frontend/package.json frontend/tsconfig.json frontend/vite.config.ts frontend/index.html ./
COPY frontend/src ./src
RUN npm install
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
