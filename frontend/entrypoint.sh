#!/bin/sh

# Start Nginx in the background
nginx &

# Wait for Nginx to start
sleep 5

# Check if a valid SSL certificate already exists and if not, obtain a new one
if [ ! -d "/etc/letsencrypt/live/sermadrid.org" ] || ! certbot certificates | grep -q "sermadrid.org"; then
    echo "Obtaining new SSL certificate for sermadrid.org"
    certbot certonly --webroot -w /usr/share/nginx/html -d sermadrid.org -d www.sermadrid.org --email begona.echavarren@gmail.com --agree-tos --non-interactive --no-eff-email
else
    echo "Existing SSL certificate found for sermadrid.org"
fi

# Add Certbot renew to crontab
echo "0 12 * * * certbot renew --webroot -w /usr/share/nginx/html" >> /etc/crontabs/root

# Rename the Nginx configuration template file, replacing the existing one
mv /etc/nginx/conf.d/default.conf.template /etc/nginx/conf.d/default.conf

# Reload Nginx to apply the new configuration and SSL certificate
nginx -s reload

# Wait for Nginx to reload
sleep 5

# Keep the container running
tail -f /dev/null
