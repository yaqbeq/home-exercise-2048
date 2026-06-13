// App entry point (like Python's `if __name__ == '__main__'`).
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/global.css' // global tokens + base styles, auto-injected by Vite
import App from './App.tsx'

// Take over the <div id="root"> from index.html and render the app into it.
// StrictMode is a dev-only wrapper that surfaces bugs; it does nothing in prod.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
