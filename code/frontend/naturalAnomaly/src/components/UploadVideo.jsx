import React from 'react';
import { Button } from '@mui/material';

const UploadVideo = ({ onUpload }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const videoURL = URL.createObjectURL(file); // יוצר URL זמני מהקובץ
      onUpload(videoURL); // שולח את זה ל־MainScreen
    }
  };

  return (
    <Button
      variant="contained"
      component="label"
    >
      העלה וידאו
      <input
        type="file"
        accept="video/*"
        hidden
        onChange={handleFileChange}
      />
    </Button>
  );
};

export default UploadVideo;
