/// <reference types="vite/client" />

// Auth configuration
export const AUTH_CONFIG = {
  DEFAULT_ADMIN: {
    username: import.meta.env.VITE_DEFAULT_ADMIN_USERNAME || 'admin',
    password: import.meta.env.VITE_DEFAULT_ADMIN_PASSWORD || 'Admin123'
  }
}