import React from 'react';
import ChatInterface from './components/ChatInterface';
import { ThemeProvider, createTheme } from '@mui/material';

const theme = createTheme({
  // You can customize your theme here if needed
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <ChatInterface />
    </ThemeProvider>
  );
}

export default App;
