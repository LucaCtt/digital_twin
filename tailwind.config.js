/** @type {import('tailwindcss').Config} */
export default {
  content: ["./frontend/**/*.{html,js}", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [require("flowbite/plugin"), require("flowbite-typography"),],
};
