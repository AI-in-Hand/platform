module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: "100ch", // add required value here
          },
        },
      },
      transitionProperty: {
        height: "height",
        spacing: "margin, padding",
      },
      backgroundColor: {
        primary: "var(--color-bg-primary)",
        secondary: "var(--color-bg-secondary)",
        accent: "var(--color-bg-accent)",
        light: "var(--color-bg-light)",
      },
      textColor: {
        accent: "var(--color-text-accent)",
        primary: "var(--color-text-primary)",
        secondary: "var(--color-text-secondary)",
      },
      borderColor: {
        accent: "var(--color-border-accent)",
        primary: "var(--color-border-primary)",
        secondary: "var(--color-border-secondary)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
