#!/bin/sh

# Start Nginx in the background
nginx &

# Wait for Nginx to start
sleep 5

# Check if a valid SSL certificate already exists and if not, obtain a new one
if [ ! -d "/etc/letsencrypt/live/${DOMAIN_NAME}" ] || ! certbot certificates | grep -q "${DOMAIN_NAME}"; then
    echo "Obtaining new SSL certificate for ${DOMAIN_NAME}"
    certbot certonly --webroot -w /usr/share/nginx/html -d "${DOMAIN_NAME}" -d "www.${DOMAIN_NAME}" --email "${CERTBOT_EMAIL}" --agree-tos --non-interactive --no-eff-email
else
    echo "Existing SSL certificate found for ${DOMAIN_NAME}"
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
