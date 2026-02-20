import type { Configuration } from 'webpack';
import { rules } from './webpack.rules';
import { plugins } from './webpack.plugins';

export const mainConfig: Configuration = {
  entry: './src/main/main.ts',
  module: {
    rules,   // ← Asset relocator is FINE here (main process only)
  },
  plugins,
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.css', '.json'],
  },
  target: 'electron-main',   // ← Important: explicitly set target
  node: {
    __dirname: false,        // ← Preserve real __dirname
    __filename: false,
  },
};
