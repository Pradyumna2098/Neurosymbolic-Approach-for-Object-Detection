import type { Configuration } from 'webpack';
import { plugins } from './webpack.plugins';

const rendererRules = [
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
  {
    test: /\.css$/,
    use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
  },
];

export const rendererConfig: Configuration = {
  module: {
    rules: rendererRules,
  },
  plugins,
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.css'],
  },
  // DO NOT set target: 'electron-renderer' here
  // electron-forge/plugin-webpack v7 sets this internally
  // Setting it explicitly causes the HMR client to use Node's require
  // which is not available in the sandboxed renderer (contextIsolation: true)
};