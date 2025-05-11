import React, { useState } from 'react';
import { Box, Typography, Modal, Paper } from '@mui/material';

const ThumbnailsLibrary = ({ thumbnails }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleThumbnailClick = (image) => {
    setSelectedImage(image);
  };

  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  return (
    <Box sx={{ marginTop: '20px' }}>
      <Typography variant="h6" gutterBottom>ספריית תמונות חום</Typography>
      <Box sx={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {thumbnails.map((thumb, index) => (
          <Box
            key={index}
            sx={{ cursor: 'pointer', width: '80px', height: '80px', overflow: 'hidden' }}
            onClick={() => handleThumbnailClick(thumb)}
          >
            <img src={thumb} alt={`Thumbnail ${index}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </Box>
        ))}
      </Box>

      {/* תצוגה מוגדלת של התמונה בלחיצה */}
      <Modal open={!!selectedImage} onClose={handleCloseModal}>
        <Paper sx={{ padding: '20px', maxWidth: '90%', maxHeight: '90%', margin: 'auto' }}>
          <img src={selectedImage} alt="Selected" style={{ width: '100%', height: 'auto' }} />
        </Paper>
      </Modal>
    </Box>
  );
};

export default ThumbnailsLibrary;
