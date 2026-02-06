import { createTheme, ThemeOptions } from '@mui/material/styles';

// Design tokens based on visual_design_guidelines.md
const darkTheme: ThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196F3',
      dark: '#1976D2',
      light: '#64B5F6',
    },
    secondary: {
      main: '#FF9800',
      dark: '#F57C00',
      light: '#FFB74D',
    },
    error: {
      main: '#F44336',
    },
    warning: {
      main: '#FF9800',
    },
    info: {
      main: '#2196F3',
    },
    success: {
      main: '#4CAF50',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
      disabled: '#6B6B6B',
    },
    divider: '#3F3F3F',
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h1: {
      fontSize: '32px',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '24px',
      fontWeight: 500,
    },
    h3: {
      fontSize: '20px',
      fontWeight: 500,
    },
    h4: {
      fontSize: '18px',
      fontWeight: 500,
    },
    h5: {
      fontSize: '16px',
      fontWeight: 500,
    },
    h6: {
      fontSize: '14px',
      fontWeight: 500,
    },
    body1: {
      fontSize: '16px',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '14px',
      lineHeight: 1.43,
    },
    button: {
      fontSize: '14px',
      fontWeight: 500,
      textTransform: 'uppercase',
    },
    caption: {
      fontSize: '12px',
      lineHeight: 1.66,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 4,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          padding: '8px 16px',
          transition: 'background 0.2s ease',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          border: '1px solid #3F3F3F',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '4px',
          },
        },
      },
    },
  },
};

const lightTheme: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#1976D2',
      dark: '#1565C0',
      light: '#42A5F5',
    },
    secondary: {
      main: '#F57C00',
      dark: '#E65100',
      light: '#FF9800',
    },
    error: {
      main: '#D32F2F',
    },
    warning: {
      main: '#F57C00',
    },
    info: {
      main: '#1976D2',
    },
    success: {
      main: '#388E3C',
    },
    background: {
      default: '#FFFFFF',
      paper: '#F5F5F5',
    },
    text: {
      primary: '#212121',
      secondary: '#666666',
      disabled: '#9E9E9E',
    },
    divider: '#E0E0E0',
  },
  typography: darkTheme.typography,
  spacing: darkTheme.spacing,
  shape: darkTheme.shape,
  components: darkTheme.components,
};

export const getDarkTheme = () => createTheme(darkTheme);
export const getLightTheme = () => createTheme(lightTheme);
