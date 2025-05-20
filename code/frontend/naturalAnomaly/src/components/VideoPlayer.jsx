import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const VideoPlayer = () => {
  const videoUrl = 'https://drive.google.com/file/d/1yldzCAxewb4NG4yhiOmjY9unFKFufhaX/preview';

  return (
    <Paper elevation={3} sx={{ padding: 2, borderRadius: 3 }}>
      <Typography variant="h6" gutterBottom>
        🎥 סרטון וידאו
      </Typography>
      <Box sx={{ width: '100%' }}>
        <iframe
          src={videoUrl}
          width="100%"
          height="400px"
          allow="autoplay"
          title="Video Player"
          style={{ border: 'none', borderRadius: '12px' }}
        ></iframe>
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
