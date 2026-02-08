/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/town_digest/app/templates/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
};
