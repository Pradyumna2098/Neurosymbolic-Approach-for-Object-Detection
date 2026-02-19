import type { Configuration } from 'webpack';

import { rules } from './webpack.rules';

export const preloadConfig: Configuration = {
  /**
   * This is the preload script for the Electron app, it's the bridge between
   * the main process and the renderer process.
   */
  module: {
    rules,
  },
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.css', '.json'],
  },
  // Preload script target - needs Node.js globals available during bundling
  target: 'electron-preload',
  // Ensure webpack doesn't replace Node.js globals
  node: {
    __dirname: false,
    __filename: false,
  },
};
