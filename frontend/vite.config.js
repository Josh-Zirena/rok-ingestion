import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    // Base public path when served in production
    base: '/',
    
    // Development server config
    server: {
      port: 3000,
      open: true,
    },
    
    // Build output directory
    build: {
      outDir: 'dist',
      sourcemap: true,
      // Clear output directory before build
      emptyOutDir: true,
    },
    
    // Define environment variables available in the app
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || ''),
    },
  }
})
