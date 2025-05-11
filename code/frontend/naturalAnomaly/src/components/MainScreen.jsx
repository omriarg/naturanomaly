import React, { useState } from 'react';
import ChatWindow from './ChatWindow.jsx';
import UploadVideo from './UploadVideo.jsx';
import VideoPlayer from './VideoPlayer.jsx';
import { Box } from '@mui/material';
import ThumbnailsLibrary from './ThumbnailsLibrary'; // ייבוא הקומפוננטה החדשה

const MainScreen = () => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [thumbnails, setThumbnails] = useState([]); // ניהול התמונות

  const handleVideoUpload = (url) => {
    setVideoUrl(url);
  };

  // פונקציה להוספת תמונת חום חדשה לספרייה
  const addThumbnail = (image) => {
    setThumbnails((prev) => [...prev, image]);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        height: '100vh',
        backgroundColor: '#f0f0f0',
      }}
    >
      {/* אזור הווידאו – צד ימין */}
      <Box
        sx={{
          flex: 2.5,
          display: 'flex',
          flexDirection: 'column',
          padding: '20px',
          gap: '20px',
          overflow: 'hidden',
        }}
      >
        <UploadVideo onUpload={handleVideoUpload} />
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <VideoPlayer videoUrl={videoUrl} />
        </Box>
      </Box>

      {/* אזור הצ'אט – צד שמאל */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: '20px',
          borderLeft: '1px solid #ccc',
          backgroundColor: '#ffffff',
        }}
      >
        <ChatWindow addThumbnail={addThumbnail} />
        <ThumbnailsLibrary thumbnails={thumbnails} />
      </Box>
    </Box>
  );
};

export default MainScreen;
