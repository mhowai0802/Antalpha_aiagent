/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sidebar: {
          DEFAULT: '#18181b',
          foreground: '#fafafa',
          muted: '#a1a1aa',
        },
      },
    },
  },
  plugins: [],
}
