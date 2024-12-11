import React, { useState } from 'react';
import { 
  Container, 
  TextField, 
  Button, 
  Paper, 
  Box,
  Typography,
  List,
  ListItem,
  ListItemText 
} from '@mui/material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatInterface = () => {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const formatMessage = (content) => {
    const isStructuredText = (text) => {
      return text.includes('**') || text.includes('*') || text.includes('#') || /\d+\./.test(text);
    };

    if (isStructuredText(content)) {
      return (
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <Typography variant="h5" sx={{ fontWeight: 'bold', mt: 2, mb: 1 }}>
                {children}
              </Typography>
            ),
            h2: ({ children }) => (
              <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 1.5, mb: 1 }}>
                {children}
              </Typography>
            ),
            ul: ({ children }) => (
              <Box component="ul" sx={{ pl: 2, my: 1 }}>
                {children}
              </Box>
            ),
            ol: ({ children }) => (
              <Box component="ol" sx={{ pl: 2, my: 1 }}>
                {children}
              </Box>
            ),
            li: ({ children, ordered }) => (
              <Box 
                component="li" 
                sx={{ 
                  my: 0.5,
                  pl: 1,
                  '& p': {
                    display: 'inline',
                    ml: 1
                  }
                }}
              >
                <Typography variant="body1">{children}</Typography>
              </Box>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      );
    }

    return <Typography variant="body1">{content}</Typography>;
  };

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile);
      const formData = new FormData();
      formData.append('file', uploadedFile);

      try {
        setLoading(true);
        await axios.post('http://localhost:5000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setLoading(false);
      } catch (error) {
        console.error('Error uploading file:', error);
        setLoading(false);
      }
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      const response = await axios.post('http://localhost:5000/query', { query });
      setMessages([...messages, 
        { type: 'user', content: query },
        { type: 'bot', content: response.data.response }
      ]);
      setQuery('');
    } catch (error) {
      console.error('Error sending query:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setMessages([]);
    axios.post('http://localhost:5000/clear')
      .catch(error => console.error('Error clearing session:', error));
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4,
          borderRadius: 2,
          backgroundColor: '#ffffff'
        }}
      >
        {/* Header Section */}
        <Box 
          sx={{ 
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 4,
            borderBottom: '1px solid #e0e0e0',
            pb: 2
          }}
        >
          <Typography 
            variant="h4" 
            sx={{ 
              fontWeight: 600,
              color: '#1976d2',
              mb: 2
            }}
          >
            PDF Chat Assistant
          </Typography>
        </Box>
        
        {/* File Upload Section */}
        <Box 
          sx={{ 
            mb: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            justifyContent: 'space-between'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="contained"
              component="label"
              sx={{ 
                borderRadius: 2,
                textTransform: 'none',
                px: 3
              }}
            >
              Upload PDF
              <input
                type="file"
                hidden
                accept=".pdf"
                onChange={handleFileUpload}
              />
            </Button>
            {file && (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#666',
                  backgroundColor: '#f5f5f5',
                  py: 1,
                  px: 2,
                  borderRadius: 1
                }}
              >
                {file.name}
              </Typography>
            )}
          </Box>
          <Button 
            variant="outlined" 
            color="error" 
            onClick={handleClear}
            disabled={loading}
            sx={{ 
              borderRadius: 2,
              textTransform: 'none'
            }}
          >
            Clear Chat
          </Button>
        </Box>

        {/* Chat Messages Section */}
        <List 
          sx={{ 
            height: '400px', 
            overflow: 'auto', 
            mb: 3,
            backgroundColor: '#fafafa',
            borderRadius: 2,
            p: 2
          }}
        >
          {messages.map((message, index) => (
            <ListItem 
              key={index} 
              sx={{
                justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                mb: 1
              }}
            >
              <Paper 
                sx={{
                  p: 2,
                  bgcolor: message.type === 'user' ? '#e3f2fd' : '#ffffff',
                  maxWidth: '80%',
                  borderRadius: message.type === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
                }}
              >
                {message.type === 'user' ? (
                  <ListItemText primary={message.content} />
                ) : (
                  formatMessage(message.content)
                )}
              </Paper>
            </ListItem>
          ))}
        </List>

        {/* Input Section */}
        <Box 
          component="form" 
          onSubmit={handleSubmit} 
          sx={{ 
            display: 'flex', 
            gap: 2,
            mt: 3
          }}
        >
          <TextField
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            disabled={loading || !query.trim()}
            sx={{ 
              borderRadius: 2,
              px: 4,
              textTransform: 'none'
            }}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatInterface; 