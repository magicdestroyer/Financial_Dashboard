FROM nginx:1.27-alpine

# Drop the default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy Nginx site config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend assets
COPY index.html    /usr/share/nginx/html/
COPY manifest.json /usr/share/nginx/html/
COPY sw.js         /usr/share/nginx/html/

# Create the icons directory so Nginx doesn't 404 on /icons/*
# Add your icon files here at build time if you have them
RUN mkdir -p /usr/share/nginx/html/icons

# Update pid file location so the non-root nginx user can write it
RUN sed -i 's|/run/nginx.pid|/tmp/nginx.pid|' /etc/nginx/nginx.conf && \
    sed -i 's|/var/run/nginx.pid|/tmp/nginx.pid|' /etc/nginx/nginx.conf && \
    # Give the nginx user ownership of cache/log dirs it needs at runtime
    chown -R nginx:nginx \
        /var/cache/nginx \
        /var/log/nginx \
        /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1
