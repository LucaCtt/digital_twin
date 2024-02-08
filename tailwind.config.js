/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./frontend/**/*.{html,js,jsx}",
    "node_modules/flowbite-react/lib/esm/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flowbite/plugin")({ charts: true }),
    require("flowbite-typography"),
  ],
};
