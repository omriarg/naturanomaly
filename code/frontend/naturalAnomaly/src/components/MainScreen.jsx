import React from 'react';
import { Box } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import HeatmapDisplay from './HeatmapDisplay';

const MainScreen = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        padding: '20px',
        backgroundColor: '#f0f0f0',
        minHeight: '100vh',
      }}
    >
      <VideoPlayer />
      <HeatmapDisplay />
    </Box>
  );
};

export default MainScreen;
