/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'noir': '#1A1A1A',
        'ivory': '#FDFCFB',
        'champagne': '#EADEDA',
        'slate-silk': '#8E8E8E',
      },
      fontFamily: {
        'display': ['"Playfair Display"', 'serif'],
        'sans': ['"Inter"', 'sans-serif'],
      },
      letterSpacing: {
        'ultra-wide': '0.15em',
      },
      borderWidth: {
        'hairline': '0.5px',
      }
    },
  },
  plugins: [],
}
