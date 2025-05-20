import React from 'react';
import ReactPlayer from 'react-player';
import { Paper, Box, Typography } from '@mui/material';

const VideoPlayer = ({ videoUrl }) => {
  console.log("Video URL:", videoUrl); // בודק אם ה-URL תקין
  if (!videoUrl) return null; // אם לא הוגדר URL, אל תציג כלום

  return (
    <Paper sx={{ padding: '10px', marginBottom: '20px' }}>
      <Typography variant="h6" gutterBottom>
        הצגת סרטון
      </Typography>
      <Box sx={{ maxWidth: '100%', display: 'flex', justifyContent: 'center' }}>
        <ReactPlayer
          url={videoUrl}
          controls={true}
          width="100%"
          height="auto"
        />
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
