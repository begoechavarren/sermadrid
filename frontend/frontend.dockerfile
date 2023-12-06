# Use an official lightweight nginx image
FROM nginx:alpine

# Set working directory to nginx asset directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy static assets over
COPY index.html index.html
COPY script.js script.js
COPY entrypoint.sh ./entrypoint.sh

# Give execution rights on the entrypoint script
RUN chmod +x ./entrypoint.sh

# Containers run nginx with global directives and daemon off
ENTRYPOINT ["./entrypoint.sh"]
