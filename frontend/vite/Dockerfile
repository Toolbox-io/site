FROM node:24

COPY frontend /root/site/frontend
COPY frontend/vite/vite.config.ts /root/site/frontend/vite.config.ts

WORKDIR /root/site/frontend
RUN --mount=type=cache,target=/root/.npm \
    rm -rf frontend/node_modules && \
    npm install && \
    npx tsc

ENTRYPOINT ["bash", "-c", "npm run dev"]