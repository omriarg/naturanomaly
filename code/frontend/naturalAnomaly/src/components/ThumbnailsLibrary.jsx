import React, { useState } from 'react';
import { Box, Typography, Modal, Paper, TextField, Button, Divider } from '@mui/material';

const ThumbnailsLibrary = ({ thumbnails, addThumbnail }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [url, setUrl] = useState('');

  const handleThumbnailClick = (image) => {
    setSelectedImage(image);
  };

  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  const handleUrlSubmit = () => {
    if (url) {
      addThumbnail(url);
      setUrl('');
    }
  };

  return (
    <Box sx={{ backgroundColor: '#f9f9f9', padding: '15px', borderRadius: '8px' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center' }}>
        🔥 תמונות חום מהסרטון
      </Typography>
      <Divider sx={{ marginBottom: '10px' }} />

      <Box
        sx={{
          display: 'grid',
          gap: '10px',
          gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
          maxHeight: '200px',
          overflowY: 'auto',
          padding: '5px',
          backgroundColor: '#e9e9e9',
          borderRadius: '8px',
        }}
      >
        {thumbnails.length > 0 ? (
          thumbnails.map((thumb, index) => (
            <Box
              key={index}
              sx={{
                cursor: 'pointer',
                borderRadius: '8px',
                overflow: 'hidden',
                '&:hover': { transform: 'scale(1.05)' },
                transition: 'transform 0.2s',
              }}
              onClick={() => handleThumbnailClick(thumb)}
            >
              <img src={thumb} alt={`Thumbnail ${index}`} style={{ width: '100%', height: '80px', objectFit: 'cover' }} />
            </Box>
          ))
        ) : (
          <Typography sx={{ textAlign: 'center', color: '#888' }}>🚫 אין תמונות חום עדיין.</Typography>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
        <TextField
          label="הוסף קישור תמונה"
          variant="outlined"
          fullWidth
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button variant="contained" color="primary" onClick={handleUrlSubmit}>
          ➕ הוסף
        </Button>
      </Box>

      <Modal open={!!selectedImage} onClose={handleCloseModal}>
        <Paper sx={{ padding: '20px', maxWidth: '90%', maxHeight: '90%', margin: 'auto', backgroundColor: '#fff' }}>
          <img src={selectedImage} alt="Selected" style={{ width: '100%', height: 'auto' }} />
        </Paper>
      </Modal>
    </Box>
  );
};

export default ThumbnailsLibrary;
