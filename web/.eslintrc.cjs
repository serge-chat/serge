const typescript = require("typescript");

module.exports = {
  root: true,
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "@typescript-eslint/parser",
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
    extraFileExtensions: [".svelte"],
    sourceType: "module",
    ecmaVersion: 2020,
  },
  extends: ["@feltjs"],
  ignorePatterns: ["*.cjs", "*.config.js"],
};
