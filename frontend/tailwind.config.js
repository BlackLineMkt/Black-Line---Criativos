/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'bl-bg':      '#0D0D0D',
        'bl-card':    '#111111',
        'bl-card-2':  '#1A1A1A',
        'bl-gold':    '#C69A3B',
        'bl-gold-2':  '#A07D2A',
        'bl-border':  '#2a2a2a',
        'bl-muted':   '#666666',
        'bl-text':    '#F0EDE8',
        'bl-red':     '#BE1919',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
      },
    },
  },
  plugins: [],
}
