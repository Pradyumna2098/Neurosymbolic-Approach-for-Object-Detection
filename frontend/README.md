# Neurosymbolic Object Detection - Frontend

Electron + React + TypeScript desktop application for neurosymbolic object detection visualization and control.

## 🚀 Quick Start

### Prerequisites

- **Node.js**: v18.x or higher (tested with v24.x)
- **npm**: v11.x or higher
- **Operating System**: Windows, macOS, or Linux

### Installation

```bash
cd frontend
npm install
```

### Development

Start the application in development mode with hot reload:

```bash
npm run dev
# or
npm start
```

### Building

Build the application for production:

```bash
npm run package
```

The packaged application will be in the `out/` directory.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main/              # Electron main process
│   │   └── main.ts        # Main process entry point
│   ├── preload/           # IPC bridge (secure)
│   │   └── preload.ts     # Preload script with contextBridge
│   └── renderer/          # React application
│       ├── App.tsx        # Main React component
│       ├── App.css        # Component styles
│       ├── index.tsx      # React entry point
│       └── index.css      # Global styles
├── .eslintrc.json         # ESLint configuration
├── .prettierrc            # Prettier configuration
├── forge.config.ts        # Electron Forge configuration
├── tsconfig.json          # TypeScript configuration
├── webpack.*.config.ts    # Webpack configurations
└── package.json           # Dependencies and scripts
```

## 🛠️ Available Scripts

| Script | Description |
|--------|-------------|
| `npm start` | Start development server with hot reload |
| `npm run dev` | Alias for `npm start` |
| `npm run package` | Package the app for current platform |
| `npm run make` | Create distributable packages |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Fix ESLint issues automatically |
| `npm run format` | Format code with Prettier |
| `npm run format:check` | Check code formatting |
| `npm run type-check` | Type check without emitting files |

## 🏗️ Technology Stack

### Core Framework
- **Electron**: v40.x - Cross-platform desktop application framework
- **React**: v18.x - UI component library
- **TypeScript**: v5.3.x - Type-safe JavaScript

### Build Tools
- **Electron Forge**: Application bundling and packaging
- **Webpack**: Module bundler with hot reload
- **Babel/SWC**: JavaScript transpilation

### Code Quality
- **ESLint**: Code linting and quality checks
- **Prettier**: Code formatting
- **TypeScript**: Static type checking

## 🔧 Configuration

### TypeScript

The project uses strict TypeScript configuration with JSX support:
- JSX mode: `react-jsx` (no need to import React in every file)
- Target: ES2020
- Strict mode enabled
- Type checking for renderer and main processes

### ESLint

Configured with:
- TypeScript ESLint parser
- Import plugin for module resolution
- Electron-specific rules
- Prettier integration (no conflicts)

### Webpack

Separate configurations for:
- **Main process**: Node.js environment
- **Renderer process**: Browser environment with React
- **Preload script**: Isolated context for IPC

## 🔐 Security

The application follows Electron security best practices:

1. **Context Isolation**: Enabled by default
2. **Node Integration**: Disabled in renderer process
3. **Preload Script**: Uses `contextBridge` for safe IPC
4. **Content Security Policy**: Configured in HTML

### IPC Communication

The preload script exposes a safe API to the renderer:

```typescript
// In renderer process
window.electronAPI.ping()  // Returns 'pong'
window.electronAPI.openFile()  // Opens file dialog
```

See `src/preload/preload.ts` for available IPC methods.

## 🎨 Development

### Hot Reload

The application supports hot module replacement in development:
- Changes to renderer code (React) reload automatically
- Changes to main process require restart
- TypeScript compilation happens on the fly

### DevTools

The DevTools are automatically opened in development mode. To disable:

Edit `src/main/main.ts`:
```typescript
// Remove or comment out:
// mainWindow.webContents.openDevTools();
```

### Adding New Features

1. **UI Components**: Add to `src/renderer/`
2. **IPC Handlers**: Add to `src/main/main.ts`
3. **IPC Methods**: Expose in `src/preload/preload.ts`

Example IPC flow:
```typescript
// 1. In main/main.ts - handle IPC
ipcMain.handle('my-action', async (event, arg) => {
  return { result: 'success' };
});

// 2. In preload/preload.ts - expose to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  myAction: (arg) => ipcRenderer.invoke('my-action', arg)
});

// 3. In renderer - use the API
const result = await window.electronAPI.myAction('data');
```

## 📦 Distribution

Create distributable packages:

```bash
npm run make
```

This creates platform-specific installers in `out/make/`:
- **Windows**: `.exe` installer (Squirrel)
- **macOS**: `.zip` archive
- **Linux**: `.deb` and `.rpm` packages

## 🧪 Testing

(Testing infrastructure to be added in future phases)

Planned test coverage:
- Unit tests with Jest
- Integration tests with Playwright
- E2E tests for main workflows

## 🐛 Troubleshooting

### Application won't start

1. Clear webpack cache: `rm -rf .webpack/`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check Node.js version: `node --version` (should be ≥18)

### Build errors

1. Run type check: `npm run type-check`
2. Run linter: `npm run lint`
3. Check webpack errors in console

### IPC not working

1. Verify preload script is loaded
2. Check `contextBridge` exposes the methods
3. Ensure `contextIsolation: true` in main process

## 📚 Documentation

- [Electron Documentation](https://www.electronjs.org/docs/latest/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Electron Forge Documentation](https://www.electronforge.io/)

## 🔄 Next Steps

As per the implementation roadmap (`docs/feature_implementation/ui_implementation_guide.md`):

### Phase 1: Foundation ✅ (Current)
- [x] Electron + React + TypeScript project initialized
- [x] Project structure created (main, preload, renderer)
- [x] TypeScript compilation working
- [x] Hot reload configured
- [x] IPC communication set up
- [x] ESLint and Prettier configured

### Phase 2: Core Features (Next)
- [ ] Implement Upload Panel
- [ ] Implement Configuration Panel
- [ ] Create basic Results Viewer
- [ ] Set up Redux state management
- [ ] Connect to backend API

## 📄 License

MIT

## 👥 Contributing

See the main repository `CONTRIBUTING.md` for contribution guidelines.
