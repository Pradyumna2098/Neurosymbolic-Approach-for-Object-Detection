import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Box,
  CssBaseline,
  Divider,
} from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import MenuIcon from '@mui/icons-material/Menu';
import { getDarkTheme, getLightTheme } from '../theme/theme';
import UploadPanel from './UploadPanel';
import ConfigPanel from './ConfigPanel';
import ResultsPanel from './ResultsPanel';
import MonitoringPanel from './MonitoringPanel';

/**
 * AppShell - Main application layout with theme provider
 * Implements four-panel layout: Upload, Config, Results, Monitoring
 * Includes menu bar and theme toggle
 */
const AppShell: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = React.useState(true);
  const [menuAnchor, setMenuAnchor] = React.useState<{
    file: null | HTMLElement;
    edit: null | HTMLElement;
    view: null | HTMLElement;
    tools: null | HTMLElement;
    help: null | HTMLElement;
  }>({
    file: null,
    edit: null,
    view: null,
    tools: null,
    help: null,
  });

  const theme = isDarkMode ? getDarkTheme() : getLightTheme();

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleMenuOpen = (menuType: keyof typeof menuAnchor) => (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor({ ...menuAnchor, [menuType]: event.currentTarget });
  };

  const handleMenuClose = (menuType: keyof typeof menuAnchor) => () => {
    setMenuAnchor({ ...menuAnchor, [menuType]: null });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* Menu Bar */}
        <AppBar position="static" elevation={1}>
          <Toolbar variant="dense">
            <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 3 }}>
              Neurosymbolic Object Detection
            </Typography>

            {/* Menu Items */}
            <Box sx={{ display: 'flex', gap: 1, flexGrow: 1 }}>
              <IconButton
                size="small"
                color="inherit"
                onClick={handleMenuOpen('file')}
                aria-label="file menu"
              >
                <MenuIcon fontSize="small" />
                <Typography variant="body2" sx={{ ml: 0.5 }}>
                  File
                </Typography>
              </IconButton>
              <Menu
                anchorEl={menuAnchor.file}
                open={Boolean(menuAnchor.file)}
                onClose={handleMenuClose('file')}
              >
                <MenuItem onClick={handleMenuClose('file')}>Open</MenuItem>
                <MenuItem onClick={handleMenuClose('file')}>Save</MenuItem>
                <Divider />
                <MenuItem onClick={handleMenuClose('file')}>Exit</MenuItem>
              </Menu>

              <IconButton
                size="small"
                color="inherit"
                onClick={handleMenuOpen('edit')}
                aria-label="edit menu"
              >
                <Typography variant="body2">Edit</Typography>
              </IconButton>
              <Menu
                anchorEl={menuAnchor.edit}
                open={Boolean(menuAnchor.edit)}
                onClose={handleMenuClose('edit')}
              >
                <MenuItem onClick={handleMenuClose('edit')}>Cut</MenuItem>
                <MenuItem onClick={handleMenuClose('edit')}>Copy</MenuItem>
                <MenuItem onClick={handleMenuClose('edit')}>Paste</MenuItem>
              </Menu>

              <IconButton
                size="small"
                color="inherit"
                onClick={handleMenuOpen('view')}
                aria-label="view menu"
              >
                <Typography variant="body2">View</Typography>
              </IconButton>
              <Menu
                anchorEl={menuAnchor.view}
                open={Boolean(menuAnchor.view)}
                onClose={handleMenuClose('view')}
              >
                <MenuItem onClick={handleMenuClose('view')}>Zoom In</MenuItem>
                <MenuItem onClick={handleMenuClose('view')}>Zoom Out</MenuItem>
                <MenuItem onClick={handleMenuClose('view')}>Reset Zoom</MenuItem>
              </Menu>

              <IconButton
                size="small"
                color="inherit"
                onClick={handleMenuOpen('tools')}
                aria-label="tools menu"
              >
                <Typography variant="body2">Tools</Typography>
              </IconButton>
              <Menu
                anchorEl={menuAnchor.tools}
                open={Boolean(menuAnchor.tools)}
                onClose={handleMenuClose('tools')}
              >
                <MenuItem onClick={handleMenuClose('tools')}>Options</MenuItem>
                <MenuItem onClick={handleMenuClose('tools')}>Settings</MenuItem>
              </Menu>

              <IconButton
                size="small"
                color="inherit"
                onClick={handleMenuOpen('help')}
                aria-label="help menu"
              >
                <Typography variant="body2">Help</Typography>
              </IconButton>
              <Menu
                anchorEl={menuAnchor.help}
                open={Boolean(menuAnchor.help)}
                onClose={handleMenuClose('help')}
              >
                <MenuItem onClick={handleMenuClose('help')}>Documentation</MenuItem>
                <MenuItem onClick={handleMenuClose('help')}>About</MenuItem>
              </Menu>
            </Box>

            {/* Theme Toggle */}
            <IconButton color="inherit" onClick={handleThemeToggle} aria-label="toggle theme">
              {isDarkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Toolbar>
        </AppBar>

        {/* Main Content Area */}
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Left Panel Container */}
          <Box
            sx={{
              width: 350,
              minWidth: 300,
              maxWidth: 500,
              display: 'flex',
              flexDirection: 'column',
              borderRight: 1,
              borderColor: 'divider',
            }}
          >
            {/* Upload Panel (Top) */}
            <Box sx={{ height: '50%', minHeight: 200, p: 1 }}>
              <UploadPanel />
            </Box>

            {/* Config Panel (Bottom) */}
            <Box sx={{ height: '50%', minHeight: 200, p: 1 }}>
              <ConfigPanel />
            </Box>
          </Box>

          {/* Right Panel Container (Results) */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Box sx={{ flex: 1, p: 1 }}>
              <ResultsPanel />
            </Box>
          </Box>
        </Box>

        {/* Bottom Monitoring Panel */}
        <MonitoringPanel />
      </Box>
    </ThemeProvider>
  );
};

export default AppShell;
