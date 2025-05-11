import React, { useState } from 'react';
import { Box, Typography, Modal, Paper, Divider } from '@mui/material';

const ThumbnailsLibrary = ({ thumbnails }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleThumbnailClick = (image) => {
    setSelectedImage(image);
  };

  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  return (
   <Box
  sx={{
    marginTop: '20px',
    backgroundColor: '#f0f4ff',  // רקע עדין לכותרת
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #1976d2'  // מסגרת לכותרת
  }}
>
  <Typography
    variant="h6"
    gutterBottom
    sx={{
      fontWeight: 'bold',
      textAlign: 'center',
      color: '#1976d2'  // צבע כותרת בולט
    }}
  >
    תמונות חום מהסרטון
  </Typography>
  <Divider sx={{ marginBottom: '10px', backgroundColor: '#1976d2' }} />

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
            boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
            transition: 'transform 0.2s, box-shadow 0.2s',
            '&:hover': {
              transform: 'scale(1.05)',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
            },
            backgroundColor: '#fff',
          }}
          onClick={() => handleThumbnailClick(thumb)}
        >
          <img
            src={thumb}
            alt={`Thumbnail ${index}`}
            style={{
              width: '100%',
              height: '80px',
              objectFit: 'cover'
            }}
          />
        </Box>
      ))
    ) : (
      <Typography sx={{ textAlign: 'center', color: '#888' }}>
        אין תמונות חום עדיין.
      </Typography>
    )}
  </Box>

  <Modal open={!!selectedImage} onClose={handleCloseModal}>
    <Paper
      sx={{
        padding: '20px',
        maxWidth: '90%',
        maxHeight: '90%',
        margin: 'auto',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
      }}
    >
      <img
        src={selectedImage}
        alt="Selected"
        style={{
          width: '100%',
          height: 'auto',
          borderRadius: '8px'
        }}
      />
    </Paper>
  </Modal>
</Box>

  );
};

export default ThumbnailsLibrary;
