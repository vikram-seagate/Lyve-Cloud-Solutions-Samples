FROM node:18-alpine3.14

WORKDIR /app

COPY package.json /app
RUN npm install --omit=dev && npm cache clean --force

COPY . /app

CMD node index.js