import React, { useState } from 'react';
import { Box, Grid, Typography, Paper } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import ChatWindow from './ChatWindow';

const MainScreen = () => {
  const [roi, setRoi] = useState(null);
  const [drawEnabled, setDrawEnabled] = useState(false);
  const [videoSize, setVideoSize] = useState({ width: 0, height: 0 });

  return (
    <Box sx={{ height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: '#f5f5f5' }}>
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', fontWeight: 'bold', pt: 2 }}>
        NATURALANOMALY – ניתוח חכם של אנומליות בזמן אמת
      </Typography>

      <Grid container spacing={2} sx={{ height: 'calc(100% - 80px)', padding: 2 }}>
        {/* צד שמאל: וידאו */}
        <Grid item xs={12} md={7} sx={{ height: '100%' }}>
          <Paper elevation={3} sx={{ height: '100%', borderRadius: 3, padding: 2 }}>
            <VideoPlayer
              roi={roi}
              setRoi={setRoi}
              drawEnabled={drawEnabled}
              setDrawEnabled={setDrawEnabled}
              setVideoSize={setVideoSize}
            />
          </Paper>
        </Grid>

        {/* צד ימין: צ'אט */}
        <Grid item xs={12} md={5} sx={{ height: '100%' }}>
          <Paper elevation={3} sx={{ height: '100%', borderRadius: 3, padding: 2 }}>
            <ChatWindow roi={roi} drawEnabled={drawEnabled} videoSize={videoSize} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MainScreen;
