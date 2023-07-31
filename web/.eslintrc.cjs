const typescript = require("typescript");

module.exports = {
  root: true,
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "@typescript-eslint/parser",
    tsconfigRootDir: __dirname,
    project: true,
    extraFileExtensions: [".svelte"],
    sourceType: "module",
    ecmaVersion: 2020,
  },
  overrides: [
    {
      files: ["*.svelte"],
      parser: "svelte-eslint-parser",
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  ],
  rules: {
    noDuplicateImports: "off",
  },
  plugins: ["@typescript-eslint"],
  extends: [
    "@feltjs",
    "eslint:recommended",
    "plugin:svelte/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/stylistic",
  ],
  ignorePatterns: ["*.cjs", "*.config.js"],
};
