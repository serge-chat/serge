/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        'rubik-pixels': ['Rubik Pixels', 'sans-serif'],
      },
    },
  },
  plugins: [require("daisyui")],
}
