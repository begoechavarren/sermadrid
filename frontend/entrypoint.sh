#!/bin/sh
# Replace the placeholder with the actual environment variable value
sed -i "s/http:\/\/\${DROPLET_IP}/http:\/\/$DROPLET_IP/g" /usr/share/nginx/html/script.js

# Start Nginx
exec nginx -g 'daemon off;'
