import type { Configuration } from 'webpack';
import { tsRule } from './webpack.rules';

export const preloadConfig: Configuration = {
  module: {
    rules: [tsRule],
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
