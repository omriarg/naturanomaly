import React, { useRef, useState, useEffect } from 'react';
import { Box, Paper, Typography, FormControlLabel, Checkbox } from '@mui/material';

const VideoPlayer = ({ roi, setRoi, drawEnabled, setDrawEnabled, setVideoSize }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPoint, setStartPoint] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');

        const draw = () => {
            if (!canvas || !ctx || !videoRef.current) return;

            // Match canvas size to video element size
            const video = videoRef.current;
            canvas.width = video.clientWidth;
            canvas.height = video.clientHeight;
            setVideoSize && setVideoSize({ width: video.clientWidth, height: video.clientHeight });
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (roi && drawEnabled) {
                ctx.strokeStyle = 'red';
                ctx.lineWidth = 2;
                ctx.strokeRect(roi.x, roi.y, roi.width, roi.height);
            }

            requestAnimationFrame(draw);
        };

        draw();
    }, [roi, drawEnabled]);

    const handleMouseDown = (e) => {
        if (!drawEnabled) return;
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setStartPoint({ x, y });
        setIsDrawing(true);
    };

    const handleMouseMove = (e) => {
        if (!isDrawing || !drawEnabled) return;
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        setRoi({
            x: Math.min(startPoint.x, x),
            y: Math.min(startPoint.y, y),
            width: Math.abs(x - startPoint.x),
            height: Math.abs(y - startPoint.y),
        });
    };

    const handleMouseUp = () => {
        if (!drawEnabled) return;
        setIsDrawing(false);
    };

    return (
        <Paper elevation={3} sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom>
                🎥 סרטון וידאו
            </Typography>

            <FormControlLabel
                control={
                    <Checkbox
                        checked={drawEnabled}
                        onChange={(e) => {
                            setDrawEnabled(e.target.checked);
                            if (!e.target.checked) setRoi(null);
                        }}
                    />
                }
                label="Draw ROI"
                sx={{ mb: 2 }}
            />

            <Box sx={{ position: 'relative', width: '100%', maxWidth: 800 }}>
                <video
                    ref={videoRef}
                    src="/routine_frame_fixed.mp4"
                    controls
                    autoPlay
                    muted
                    playsInline
                    style={{ width: '100%', height: '450px', borderRadius: '12px', display: 'block' }}
                    onError={(e) => {
                        const videoEl = e.currentTarget;
                        if (videoEl.error) {
                            console.error('MediaError code:', videoEl.error.code);
                            switch(videoEl.error.code) {
                                case 1:
                                    console.error('MEDIA_ERR_ABORTED: fetching process aborted by user');
                                    break;
                                case 2:
                                    console.error('MEDIA_ERR_NETWORK: error occurred when downloading');
                                    break;
                                case 3:
                                    console.error('MEDIA_ERR_DECODE: error occurred when decoding');
                                    break;
                                case 4:
                                    console.error('MEDIA_ERR_SRC_NOT_SUPPORTED: media not supported');
                                    break;
                                default:
                                    console.error('Unknown media error');
                            }
                        }
                    }}
                />
                {drawEnabled && (
                    <canvas
                        ref={canvasRef}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            zIndex: 10,
                            cursor: 'crosshair',
                            width: '100%',
                            height: '450px',
                            borderRadius: '12px',
                        }}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                    />
                )}
            </Box>
        </Paper>
    );
};

export default VideoPlayer;
