import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  // Server-only variable: no credentials or backend environment reach the browser.
  const env = loadEnv(mode, process.cwd(), 'BACKEND_');
  const proxy = {
    '/api': {
      target: env.BACKEND_URL || 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
      timeout: 12000,
      proxyTimeout: 12000,
    },
  };
  return {
    server: { host: '127.0.0.1', port: 5173, strictPort: true, proxy },
    preview: { host: '127.0.0.1', port: 4173, strictPort: true, proxy },
  };
});
