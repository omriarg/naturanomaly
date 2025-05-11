import React, { useState } from 'react';
import ChatWindow from './ChatWindow.jsx';
import UploadVideo from './UploadVideo.jsx';
import VideoPlayer from './VideoPlayer.jsx';
import { Box } from '@mui/material';
import ThumbnailsLibrary from './ThumbnailsLibrary';

const MainScreen = () => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [thumbnails, setThumbnails] = useState([]);

  const handleVideoUpload = (url) => {
    setVideoUrl(url);
  };

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

      <Box
        sx={{
          flex: 1,
          padding: '20px',
          borderLeft: '1px solid #ccc',
          backgroundColor: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        <ChatWindow addThumbnail={addThumbnail} />
        <ThumbnailsLibrary thumbnails={thumbnails} />
      </Box>
    </Box>
  );
};

export default MainScreen;
