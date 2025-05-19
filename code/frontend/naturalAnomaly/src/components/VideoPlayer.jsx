import React from 'react';
import { Paper, Box, Typography } from '@mui/material';

const VideoPlayer = () => {
  const videoUrl = 'https://drive.google.com/file/d/1yldzCAxewb4NG4yhiOmjY9unFKFufhaX/preview';

  console.log("Video URL:", videoUrl);  // הצגת נתיב הסרטון בקונסול

  return (
    <Paper sx={{ padding: '10px', marginBottom: '20px' }}>
      <Typography variant="h6" gutterBottom>
        🎥 הצגת סרטון
      </Typography>
      <Box sx={{ maxWidth: '100%', display: 'flex', justifyContent: 'center' }}>
        <iframe
          src={videoUrl}
          width="100%"
          height="500px"
          allow="autoplay"
          title="Video Player"
        ></iframe>
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
