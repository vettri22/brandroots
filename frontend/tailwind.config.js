/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070D18',
          900: '#0A1424',
          850: '#0E1B31',
          800: '#14233F',
          700: '#1E355F',
        },
        charcoal: {
          900: '#111827',
          800: '#1F2937',
          700: '#374151',
          600: '#4B5563',
        },
        teal: {
          500: '#14B8A6',
          400: '#2DD4BF',
          300: '#5EEAD4',
          900: '#134E4A',
        },
        cyan: {
          500: '#06B6D4',
          400: '#22D3EE',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
