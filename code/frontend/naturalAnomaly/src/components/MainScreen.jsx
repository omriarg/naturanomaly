import React, { useState } from 'react';
import ChatWindow from './ChatWindow';
import UploadVideo from './UploadVideo';
import VideoPlayer from './VideoPlayer';
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
        padding: '20px',
        gap: '20px',
      }}
    >
      {/* אזור הווידאו – צד ימין */}
      <Box
        sx={{
          flex: 2.5,
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#ffffff',
          padding: '15px',
          borderRadius: '10px',
        }}
      >
        {videoUrl ? (
          <VideoPlayer videoUrl={videoUrl} />
        ) : (
          <Box sx={{ textAlign: 'center', color: '#888' }}>
            📽️ מחכה לסרטון שלך כאן!
          </Box>
        )}
        <UploadVideo onUpload={handleVideoUpload} />
      </Box>

      {/* אזור הצ'אט והספרייה – צד שמאל */}
      <Box
        sx={{
          flex: 1.5,
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
        }}
      >
        <ChatWindow />
        <ThumbnailsLibrary thumbnails={thumbnails} addThumbnail={addThumbnail} />
      </Box>
    </Box>
  );
};

export default MainScreen;
