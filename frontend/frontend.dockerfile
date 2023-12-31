# Use an official lightweight nginx image
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy static assets
COPY index.html /usr/share/nginx/html/index.html
COPY script.js /usr/share/nginx/html/script.js
COPY entrypoint.sh ./entrypoint.sh

# Configure the Nginx reverse proxy
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Give execution rights on the entrypoint script
RUN chmod +x ./entrypoint.sh

# Containers run nginx with global directives and daemon off
ENTRYPOINT ["./entrypoint.sh"]
