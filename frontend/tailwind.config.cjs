/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          beige: '#F5F3EE',
          terracotta: '#D97A4A',
          forest: '#2F4D35',
          sky: '#A7D0E6',
          graphite: '#3D3D3D',
          // Legacy aliases for gradual migration
          mint: '#2F4D35',
          mint100: '#F5F3EE'
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji']
      }
    }
  },
  plugins: []
}
