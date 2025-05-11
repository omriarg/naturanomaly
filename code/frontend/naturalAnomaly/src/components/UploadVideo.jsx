import React, { useState } from 'react';
import { Button, TextField, Box, Typography } from '@mui/material';

const UploadVideo = ({ onUpload }) => {
  const [videoURL, setVideoURL] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const videoURL = URL.createObjectURL(file);
      onUpload(videoURL);
    }
  };

  const handleURLUpload = () => {
    if (videoURL.trim() !== '') {
      onUpload(videoURL);
      setVideoURL('');
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <Button
        variant="contained"
        component="label"
        sx={{ backgroundColor: '#007bff', '&:hover': { backgroundColor: '#0056b3' } }}
      >
        🎥 העלה סרטון מהמחשב שלך!
        <input
          type="file"
          accept="video/*"
          hidden
          onChange={handleFileChange}
        />
      </Button>

      <Box sx={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <TextField
          fullWidth
          label="🌐 תן לנו קישור לסרטון שלך!"
          variant="outlined"
          value={videoURL}
          onChange={(e) => setVideoURL(e.target.value)}
        />
        <Button
          variant="contained"
          onClick={handleURLUpload}
          sx={{ backgroundColor: '#28a745', '&:hover': { backgroundColor: '#218838' } }}
        >
          🚀 העלה URL
        </Button>
      </Box>
    </Box>
  );
};

export default UploadVideo;
