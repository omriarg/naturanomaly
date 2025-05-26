import React, { useState } from 'react';
import { Box, Grid, Typography, Paper } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import HeatmapDisplay from './HeatmapDisplay';
import ChatWindow from './ChatWindow';

const MainScreen = () => {
    const [roi, setRoi] = useState(null);
    const [drawEnabled, setDrawEnabled] = useState(false);
    const [videoSize, setVideoSize] = useState({ width: 0, height: 0 });
    return (
        <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: 3 }}>
            <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', fontWeight: 'bold' }}>
                NATURALANOMALY – ניתוח חכם של אנומליות בזמן אמת
            </Typography>

            <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, marginBottom: 3 }}>
                <VideoPlayer
                    roi={roi}
                    setRoi={setRoi}
                    drawEnabled={drawEnabled}
                    setDrawEnabled={setDrawEnabled}
                    setVideoSize={setVideoSize}
                />
            </Paper>

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, height: '100%' }}>
                        <HeatmapDisplay />
                    </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ padding: 2, borderRadius: 3, height: '100%' }}>
                        <ChatWindow roi={roi} drawEnabled={drawEnabled} videoSize={videoSize} />
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default MainScreen;
