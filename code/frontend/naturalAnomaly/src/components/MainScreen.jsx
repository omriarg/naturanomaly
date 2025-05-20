import React from 'react';
import { Box, Grid, Typography, Paper } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import HeatmapDisplay from './HeatmapDisplay';
import ChatWindow from './ChatWindow';

const MainScreen = () => {
  return (
    <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: 3 }}>
      {/* כותרת עליונה */}
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', fontWeight: 'bold' }}>
        NaturalAnomaly - your AI ass
      </Typography>

      {/* וידאו */}
      <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, marginBottom: 3 }}>
        <VideoPlayer />
      </Paper>

      {/* Heatmap + Chat */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, height: '100%' }}>
            <HeatmapDisplay />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, height: '100%' }}>
            <ChatWindow />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MainScreen;
