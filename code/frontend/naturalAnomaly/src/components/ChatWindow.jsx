import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Paper, Typography, Button } from '@mui/material';

// CSRF token function unchanged
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

const ChatWindow = ({ roi,videoSize }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const isRoiChecked = roi && roi.width > 0 && roi.height > 0;

  const sendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage = { sender: 'user', content: inputMessage };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputMessage('');

    if (isRoiChecked) {
      const scaleX = 1280 / videoSize.width;
      const scaleY = 720 / videoSize.height;
      const scaledbbox = [
        Math.round(roi.x * scaleX),
        Math.round(roi.y * scaleY),
        Math.round((roi.x + roi.width) * scaleX),
        Math.round((roi.y + roi.height) * scaleY),
      ];
      // ROI is active, send to a different API endpoint with bbox info
      fetch('api/query-ollama-inROI', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          message: inputMessage,
          bbox: scaledbbox
        }),
      })
          .then((response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
          })
          .then((data) => {
            const botMessage = {
              sender: 'bot',
              content: data.response || 'הבוט לא החזיר תשובה.',
            };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
          })
          .catch((error) => {
            console.error('Error:', error);
            setMessages((prevMessages) => [
              ...prevMessages,
              { sender: 'bot', content: 'שגיאה בשרת, נסה שוב מאוחר יותר.' },
            ]);
          });

    } else {
      // ROI not active, keep existing behavior
      fetch('/api/query-ollama/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ message: inputMessage }),
      })
          .then((response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
          })
          .then((data) => {
            const botMessage = {
              sender: 'bot',
              content: data.response || 'הבוט לא החזיר תשובה.',
            };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
          })
          .catch((error) => {
            console.error('Error:', error);
            setMessages((prevMessages) => [
              ...prevMessages,
              { sender: 'bot', content: 'שגיאה בשרת, נסה שוב מאוחר יותר.' },
            ]);
          });
    }
  };

  return (
      <Paper sx={{ padding: '20px', height: '300px', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flex: 1, overflowY: 'auto' }}>
          {messages.map((msg, index) => (
              <Typography key={index} variant="body2" sx={{ marginBottom: '5px' }}>
                {msg.sender === 'user' ? '👤 אתה: ' : '🤖 הבוט: '} {msg.content}
              </Typography>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        <TextField
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            fullWidth
            variant="outlined"
            placeholder="💬 כתוב כאן..."
            sx={{ marginTop: '10px' }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') sendMessage();
            }}
        />
        <Button onClick={sendMessage} variant="contained" sx={{ marginTop: '10px' }}>
          שלח
        </Button>
      </Paper>
  );
};

export default ChatWindow;