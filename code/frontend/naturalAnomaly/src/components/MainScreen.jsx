import React, { useState } from 'react';
import ChatWindow from './ChatWindow.jsx';
import UploadVideo from './UploadVideo.jsx';
import VideoPlayer from './VideoPlayer.jsx';
import { Box, Button, CircularProgress } from '@mui/material';
import ThumbnailsLibrary from './ThumbnailsLibrary';

const MainScreen = () => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [thumbnails, setThumbnails] = useState([]);
  const [loading, setLoading] = useState(false); // מצב טעינה

  const handleVideoUpload = (url) => {
    setVideoUrl(url);
  };

  // פונקציה להוספת תמונה לספרייה
  const addThumbnail = (image) => {
    setThumbnails((prev) => [...prev, image]);
  };

  // שליחת בקשה לשרת לקבלת תמונת חום
  const fetchHeatmapImage = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/generate-heatmap/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ videoUrl }), // כאן אתה יכול לשלוח את כתובת הווידאו לשרת
      });

      if (!response.ok) {
        throw new Error(`שגיאה בשרת: ${response.status}`);
      }

      const data = await response.json();
      if (data.image) {
        addThumbnail(data.image); // מוסיף את תמונת החום לספרייה
      } else {
        console.error("לא התקבלה תמונה מהשרת.");
      }
    } catch (error) {
      console.error("שגיאה בעת שליחת בקשה לשרת:", error);
    } finally {
      setLoading(false);
    }
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
        <Box sx={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={fetchHeatmapImage}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "צור תמונת חום"}
          </Button>
        </Box>
      </Box>

      {/* אזור הצ'אט – צד שמאל */}
      <Box
        sx={{
          flex: 1,
          padding: '20px',
          borderLeft: '1px solid #ccc',
          backgroundColor: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <ChatWindow />
        <ThumbnailsLibrary thumbnails={thumbnails} />
      </Box>
    </Box>
  );
};

export default MainScreen;
