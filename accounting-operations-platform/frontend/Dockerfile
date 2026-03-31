FROM node:20-alpine
WORKDIR /usr/src/app
COPY package.json tsconfig.json vite.config.ts ./
COPY src ./src
RUN npm install
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
