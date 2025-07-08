FROM node:20

COPY frontend /root/site/frontend
COPY frontend/vite/vite.config.ts /root/site/frontend/vite.config.ts

WORKDIR /root/site/frontend
RUN npx tsc && npm ci

ENTRYPOINT exec npx \
    vite \
    --port 8002 \
    --host \
    --strictPort \
    --open false