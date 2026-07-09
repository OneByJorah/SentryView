import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite config (migrated from Create React App).
// Output dir kept as "build" so the Dockerfile/nginx COPY paths stay unchanged.
// CRA allowed JSX inside .js files; configure esbuild to do the same.
export default defineConfig({
  plugins: [react({ include: /\.(js|jsx)$/ })],
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.js$/,
    exclude: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
  build: {
    outDir: 'build',
  },
  server: {
    host: true,
    port: 3000,
  },
  preview: {
    host: true,
    port: 3000,
  },
});
