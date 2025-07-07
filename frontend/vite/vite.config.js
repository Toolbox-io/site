import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/guides': 'http://localhost:8000',
            '/api': 'http://localhost:8000',
        },
    },
});
