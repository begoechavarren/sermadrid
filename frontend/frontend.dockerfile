# Use an official lightweight nginx image
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy static assets
COPY index.html /usr/share/nginx/html/index.html
COPY script.js /usr/share/nginx/html/script.js

# Configure the Nginx reverse proxy
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Containers run nginx with global directives and daemon off
CMD ["nginx", "-g", "daemon off;"]
