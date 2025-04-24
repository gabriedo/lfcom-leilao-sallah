import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    root: '.',
    base: './',
    server: {
      port: 8083,
      host: '0.0.0.0',
      strictPort: true,
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_SCRAPHUB_API_URL,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('proxy error', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('Sending Request to the Target:', {
                method: req.method,
                url: req.url,
                target: env.VITE_SCRAPHUB_API_URL
              });
              const apiKey = env.VITE_SCRAPHUB_API_KEY;
              if (apiKey) {
                proxyReq.setHeader('Authorization', `Bearer ${apiKey}`);
                console.log('Authorization header added');
              } else {
                console.warn('API key not found in environment variables');
              }
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Received Response from the Target:', {
                statusCode: proxyRes.statusCode,
                url: req.url,
                headers: proxyRes.headers
              });
            });
          }
        }
      }
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom'],
      exclude: ['venv', 'node_modules'],
    },
  };
}); 