module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }],
    '@babel/preset-typescript',
  ],
  plugins: [
    // Vite's `import.meta.env.*` has no meaning to Jest/CommonJS — rewrite
    // it to `process.env.*` so client.ts's env lookup still works in tests.
    'transform-vite-meta-env',
  ],
}
