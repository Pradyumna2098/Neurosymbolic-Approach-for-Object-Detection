import type { Configuration } from 'webpack';

// Preload-specific rules — NO asset relocator loader
const preloadRules = [
  {
    test: /\.tsx?$/,
    exclude: /(node_modules|\.webpack)/,
    use: {
      loader: 'ts-loader',
      options: {
        transpileOnly: true,
      },
    },
  },
];

export const preloadConfig: Configuration = {
  module: {
    rules: preloadRules,
  },
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.css', '.json'],
  },
  target: 'electron-preload',
  node: {
    __dirname: false,
    __filename: false,
  },
};
