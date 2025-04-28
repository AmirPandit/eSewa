FROM node:20.11-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

RUN npm install -g serve

EXPOSE 4200

CMD ["serve", "-s", "dist/frontend/browser/", "-l", "4200"]
