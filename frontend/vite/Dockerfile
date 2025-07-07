FROM node:24

COPY frontend /root/site/frontend
COPY frontend/vite/vite.config.js /root/site/frontend/vite.config.js

WORKDIR /root/site/frontend
ENTRYPOINT exec npx \
    --node-options="--es-module-specifier-resolution=node" \
    vite \
    --port 8002 \
    --strictPort \
    --open false