import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Paper, Typography, Button, Modal } from '@mui/material';

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

const ChatWindow = ({ roi, videoSize }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [openImage, setOpenImage] = useState(null); // 🔥 תמונה לפתיחה ב-modal
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

    const handleResponse = (data) => {
      let botMessage;
      if (data.image) {
        botMessage = {
          sender: 'bot',
          content: '',
          image: `data:image/png;base64,${data.image}`,
        };
      } else {
        botMessage = {
          sender: 'bot',
          content: data.response || 'הבוט לא החזיר תשובה.',
        };
      }
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    };

    const handleError = (error) => {
      console.error('Error:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', content: 'שגיאה בשרת, נסה שוב מאוחר יותר.' },
      ]);
    };

    const endpoint = isRoiChecked ? 'api/query-ollama-inROI' : '/api/query-ollama/';
    const payload = isRoiChecked
      ? {
          message: inputMessage,
          bbox: [
            Math.round(roi.x * (1280 / videoSize.width)),
            Math.round(roi.y * (720 / videoSize.height)),
            Math.round((roi.x + roi.width) * (1280 / videoSize.width)),
            Math.round((roi.y + roi.height) * (720 / videoSize.height)),
          ],
        }
      : { message: inputMessage };

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify(payload),
    })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then(handleResponse)
      .catch(handleError);
  };

  return (
    <>
      <Paper sx={{ padding: '20px', height: '300px', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flex: 1, overflowY: 'auto' }}>
          {messages.map((msg, index) => (
            <Box key={index} sx={{ marginBottom: '10px' }}>
              {msg.sender === 'user' ? (
                <Typography variant="body2">👤 אתה: {msg.content}</Typography>
              ) : msg.image ? (
                <>
                  <Typography variant="body2">🤖 הבוט שלח תמונה (לחץ להגדלה):</Typography>
                  <img
                    src={msg.image}
                    alt="Heatmap"
                    onClick={() => setOpenImage(msg.image)}
                    style={{
                      maxWidth: '100%',
                      maxHeight: '200px',
                      borderRadius: '8px',
                      marginTop: '5px',
                      cursor: 'pointer',
                      transition: 'transform 0.2s',
                    }}
                    onMouseOver={(e) => (e.currentTarget.style.transform = 'scale(1.02)')}
                    onMouseOut={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
                  />
                </>
              ) : (
                <Typography variant="body2">🤖 הבוט: {msg.content}</Typography>
              )}
            </Box>
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

      {/* 🔍 Modal להצגת תמונה בגודל מלא */}
      <Modal open={!!openImage} onClose={() => setOpenImage(null)}>
        <Box
          onClick={() => setOpenImage(null)}
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            bgcolor: 'rgba(0,0,0,0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            cursor: 'zoom-out',
            zIndex: 9999,
          }}
        >
          <img
            src={openImage}
            alt="הגדלה"
            style={{
              maxWidth: '90%',
              maxHeight: '90%',
              borderRadius: '12px',
              boxShadow: '0 0 20px rgba(255,255,255,0.3)',
            }}
          />
        </Box>
      </Modal>
    </>
  );
};

export default ChatWindow;
