const typescript = require('typescript');

module.exports = {
	root: true,
	parser: '@typescript-eslint/parser',
	parserOptions: {
		tsconfigRootDir: __dirname,
		project: ['./tsconfig.json'],
		extraFileExtensions: ['.svelte'],
		sourceType: 'module',
		ecmaVersion: 2020,
	},
    extends: [
        "@feltjs"
    ]
}