FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src
COPY scripts ./scripts

RUN npm run build

EXPOSE 4000
CMD ["npm", "start"]
