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
  openModelFile: () => ipcRenderer.invoke('dialog:openModelFile'),
  openPrologFile: () => ipcRenderer.invoke('dialog:openPrologFile'),

  // Export file dialogs
  saveFile: (options: {
    title?: string;
    defaultPath?: string;
    filters?: { name: string; extensions: string[] }[];
  }) => ipcRenderer.invoke('dialog:saveFile', options),
  saveImage: (defaultPath?: string) => ipcRenderer.invoke('dialog:saveImage', defaultPath),
  saveCSV: (defaultPath?: string) => ipcRenderer.invoke('dialog:saveCSV', defaultPath),
  saveJSON: (defaultPath?: string) => ipcRenderer.invoke('dialog:saveJSON', defaultPath),

  // Event listeners with unsubscribe capability
  onUpdateAvailable: (callback: () => void) => {
    ipcRenderer.on('update-available', callback);
    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener('update-available', callback);
    };
  },

  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  },
});

// Type definitions for TypeScript
export interface ElectronAPI {
  ping: () => Promise<string>;
  openFile: () => Promise<string | null>;
  openModelFile: () => Promise<string | null>;
  openPrologFile: () => Promise<string | null>;
  saveFile: (options: {
    title?: string;
    defaultPath?: string;
    filters?: { name: string; extensions: string[] }[];
  }) => Promise<string | null>;
  saveImage: (defaultPath?: string) => Promise<string | null>;
  saveCSV: (defaultPath?: string) => Promise<string | null>;
  saveJSON: (defaultPath?: string) => Promise<string | null>;
  onUpdateAvailable: (callback: () => void) => () => void;
  removeAllListeners: (channel: string) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
