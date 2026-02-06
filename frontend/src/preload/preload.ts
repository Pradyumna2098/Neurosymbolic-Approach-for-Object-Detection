// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Example IPC methods - these can be expanded as needed
  ping: () => ipcRenderer.invoke('ping'),

  // File system operations
  openFile: () => ipcRenderer.invoke('dialog:openFile'),

  // Event listeners
  onUpdateAvailable: (callback: () => void) => {
    ipcRenderer.on('update-available', callback);
  },

  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  },
});

// Type definitions for TypeScript
export interface ElectronAPI {
  ping: () => Promise<string>;
  openFile: () => Promise<string>;
  onUpdateAvailable: (callback: () => void) => void;
  removeAllListeners: (channel: string) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
