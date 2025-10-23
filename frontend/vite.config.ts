import { defineConfig } from 'vite'
import { resolve } from 'path'
import { existsSync } from 'fs'

export default defineConfig({
    server: {
        port: 8001,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    },
    plugins: [
        {
            name: 'directory-routing',
            configureServer(server) {
                server.middlewares.use((req, res, next) => {
                    // Handle directory-based routing for paths like /guides
                    if (req.url && !req.url.includes('.') && !req.url.startsWith('/api/')) {
                        const url = req.url.endsWith('/') ? req.url.slice(0, -1) : req.url
                        
                        // Try to find matching HTML files
                        const possiblePaths = [
                            `${url}.html`,
                            `${url}/index.html`
                        ]
                        
                        for (const path of possiblePaths) {
                            const fullPath = resolve(process.cwd(), path.slice(1))
                            if (existsSync(fullPath)) {
                                req.url = path
                                break
                            }
                        }
                    }
                    next()
                })
            }
        }
    ],
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
        sourcemap: false,
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'index.html'),
                guides: resolve(__dirname, 'guides/index.html'),
                account: resolve(__dirname, 'account/index.html'),
                download: resolve(__dirname, 'download.html'),
                support: resolve(__dirname, 'support.html'),
                error401: resolve(__dirname, 'error/401or403.html'),
                error404: resolve(__dirname, 'error/404.html')
            }
        }
    },
    appType: 'mpa'
})