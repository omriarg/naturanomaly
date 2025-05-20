import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const HeatmapDisplay = () => {
  const heatmapUrl = `${import.meta.env.BASE_URL}heat_map_display.png`;

  return (
    <Paper sx={{ padding: '10px', marginTop: '20px' }}>
      <Typography variant="h6" gutterBottom>
        🔥 מפת חום
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img
          src={heatmapUrl}
          alt="Heatmap"
          style={{ maxWidth: '100%', borderRadius: '8px' }}
        />
      </Box>
    </Paper>
  );
};

export default HeatmapDisplay;
