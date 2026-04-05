<<<<<<< HEAD
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        blood: {
          50: '#fff1f2',
          100: '#ffe4e6',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
=======
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#0b4f6c",
        accent: "#1f8ea3",
        critical: "#b00020",
        high: "#e07a1f",
        medium: "#c9a227",
        low: "#3d5a80",
      },
      boxShadow: {
        card: "0 10px 30px rgba(15, 23, 42, 0.08)",
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
      },
    },
  },
  plugins: [],
<<<<<<< HEAD
}
=======
};
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
