import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Paper, Typography, Button } from '@mui/material';

const ChatWindow = ({ addThumbnail }) => {
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
      },
      body: JSON.stringify({ message: inputMessage }),
    })
      .then((res) => res.json())
      .then((data) => {
        const botMessage = {
          sender: 'bot',
          content: data.response,
        };
        setMessages((prevMessages) => [...prevMessages, botMessage]);

        if (data.image) {
          addThumbnail(data.image);
        }
      })
      .catch((error) => {
        console.error('Fetch error:', error);
        setMessages((prevMessages) => [...prevMessages, { sender: 'bot', content: 'שגיאה בשרת, נסה שוב מאוחר יותר.' }]);
      });
  }, [inputMessage, addThumbnail]);

  return (
    <Paper sx={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flex: 1, overflowY: 'auto', marginBottom: '10px' }}>
        {messages.map((msg, index) => (
          <Typography key={index} variant="body1" sx={{ margin: '5px 0', fontWeight: msg.sender === 'user' ? 'bold' : 'normal' }}>
            {msg.sender === 'user' ? 'אתה: ' : 'הבוט: '} {msg.content}
          </Typography>
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
      <Button onClick={sendMessage} variant="contained" fullWidth>שלח</Button>
    </Paper>
  );
};

export default ChatWindow;
