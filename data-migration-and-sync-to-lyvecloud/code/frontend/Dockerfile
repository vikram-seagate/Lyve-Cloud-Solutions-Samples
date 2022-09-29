FROM node:18-alpine3.14

WORKDIR /app

COPY package.json /app
RUN npm install && npm cache clean --force

COPY . /app

CMD npm start
EXPOSE 3000


