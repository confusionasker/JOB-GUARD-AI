/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        risk: {
          low: '#10b981',       // Green
          moderate: '#f59e0b',  // Amber
          suspicious: '#f97316',// Orange
          high: '#ef4444',      // Red
        }
      }
    },
  },
  plugins: [],
}

