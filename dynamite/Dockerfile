FROM node:alpine
WORKDIR /app
COPY package.json ./
COPY package-lock.json ./
RUN npm install -y 
COPY src/ ./src/
COPY tsconfig.json ./
EXPOSE 8080
RUN npx tsc
CMD ["node", "dist/dynamite.js"]