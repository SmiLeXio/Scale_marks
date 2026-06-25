/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        ink: '#17211b',
        moss: '#5c6f4a',
        fern: '#7a8f62',
        clay: '#b9734f',
        shell: '#f3efe4',
        bone: '#fbfaf5',
        water: '#4f8c8b'
      },
      fontFamily: {
        sans: ['Aptos', 'Segoe UI', 'Noto Sans SC', 'sans-serif']
      },
      boxShadow: {
        soft: '0 18px 45px rgba(23, 33, 27, 0.10)'
      }
    }
  },
  plugins: []
}
