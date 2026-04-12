/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'display': ['Poppins', 'sans-serif'],
        'serif': ['Source Serif 4', 'serif'],
      },
      colors: {
        'text-white': 'hsl(0, 0%, 100%)',
      },
      borderRadius: {
        '3xl': '1.875rem',
        '2.5rem': '2.5rem',
      },
      spacing: {
        'inset-4': '1rem',
        'inset-6': '1.5rem',
      },
      letterSpacing: {
        'tighter': '-0.05em',
        'widest': '0.2em',
      },
    },
  },
  plugins: [],
}
