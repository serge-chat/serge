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
  overrides: [
    {
      files: ["*.svelte"],
      parser: "svelte-eslint-parser",
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  ],
  extends: ["@feltjs", "plugin:svelte/recommended", "plugin:@typescript-eslint/recommended"],
  ignorePatterns: ["*.cjs", "*.config.js"],
};
