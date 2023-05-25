/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        'rubik-pixels': ['Rubik Pixels', 'cursive'],
      },
    },
  },
  plugins: [require("daisyui")],
}
