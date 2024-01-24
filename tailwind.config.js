/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./dt/frontend/**/*.{html,js}", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [require("flowbite/plugin")],
};
