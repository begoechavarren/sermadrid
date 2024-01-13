# Build the Vue.js application

FROM node:lts-alpine as build-stage

WORKDIR /app

ARG MAPBOX_TOKEN

COPY package*.json ./

RUN npm install

RUN echo "VUE_APP_MAPBOX_TOKEN=${MAPBOX_TOKEN}" > .env

COPY . .

RUN npm run build


# Serve the app with Nginx

FROM nginx:stable-alpine as production-stage

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build-stage /app/dist /usr/share/nginx/html

COPY nginx/nginx-initial.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
