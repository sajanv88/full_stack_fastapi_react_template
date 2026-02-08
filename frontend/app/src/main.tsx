import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import { ThemeProvider } from './components/providers/theme-provider.tsx'
import './index.css'
import { BrowserRouter } from "react-router";
import { AuthProvider } from './components/providers/auth-provider.tsx'
import { AppConfigProvider } from '@/components/providers/app-config-provider.tsx'
import { BrandingProvider } from '@/components/providers/branding-provider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename='/'>
      <AuthProvider>
        <AppConfigProvider>
          <BrandingProvider>
            <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
              <App />
            </ThemeProvider>
          </BrandingProvider>
        </AppConfigProvider>
      </AuthProvider>
    </BrowserRouter>

  </StrictMode>,
)
