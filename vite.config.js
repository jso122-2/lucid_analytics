// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  // Specify the root if needed (default is process.cwd())
  root: './src',
  build: {
    outDir: resolve(__dirname, 'dist'),
    // Empty outDir before build if needed:
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/index.html')
      }
    }
  }
});
