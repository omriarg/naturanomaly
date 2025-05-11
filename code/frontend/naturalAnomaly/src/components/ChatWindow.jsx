import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Paper, Typography, Button } from '@mui/material';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const handleInputChange = useCallback((event) => {
    setInputMessage(event.target.value);
  }, []);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

const sendMessage = useCallback(() => {
  if (inputMessage.trim() === '') return;

  const newMessage = {
    sender: 'user',
    content: inputMessage,
  };

  setMessages((prevMessages) => [...prevMessages, newMessage]);
  setInputMessage('');

  fetch('api/query-ollama/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ message: inputMessage }),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      const botMessage = {
        sender: 'bot',
        content: data.response,
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // אם ההודעה מהבוט היא תמונה - הוסף לספריית התמונות
      if (data.image) {
        addThumbnail(data.image); // כאן אנו מוסיפים את התמונה
      }
    })
    .catch((error) => {
      console.error('Fetch error:', error);
      const errorMessage = {
        sender: 'bot',
        content: 'שגיאה בשרת, נסה שוב מאוחר יותר.',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    });
}, [inputMessage]);

  return (
    <Paper sx={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flex: 1, overflowY: 'auto', marginBottom: '10px' }}>
        {messages.map((msg, index) => (
          <Box key={index} sx={{ display: 'flex', marginBottom: '10px' }}>
            <Typography variant="body1" sx={{ fontWeight: msg.sender === 'user' ? 'bold' : 'normal' }}>
              {msg.sender === 'user' ? 'אתה: ' : 'הבוט: '} {msg.content}
            </Typography>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>
      <TextField
        value={inputMessage}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        label="הקלד הודעה"
        sx={{ marginBottom: '10px' }}
      />
      <Button onClick={sendMessage} variant="contained" fullWidth>
        שלח
      </Button>
    </Paper>
  );
};

export default ChatWindow;
