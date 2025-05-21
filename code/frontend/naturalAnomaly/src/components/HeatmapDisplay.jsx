import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const HeatmapDisplay = () => {
  const heatmapUrl = 'https://i.imgur.com/oJ1G7gG.jpeg';

  return (
    <Paper elevation={3} sx={{ padding: 2, borderRadius: 3 }}>
      <Typography variant="h6" gutterBottom>
        🌡️ Heatmap
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img
          src={heatmapUrl}
          alt="Heatmap"
          style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '12px' }}
        />
      </Box>
    </Paper>
  );
};

export default HeatmapDisplay;
