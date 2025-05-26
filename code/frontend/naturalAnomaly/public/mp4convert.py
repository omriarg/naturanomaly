import ffmpeg
import os

# Set the full path to ffmpeg.exe
os.environ['PATH'] += os.pathsep + r'C:\Users\omria\Downloads\ffmpeg-2025-05-21-git-4099d53759-full_build\ffmpeg-2025-05-21-git-4099d53759-full_build\bin'

def convert_to_web_compatible(input_path, output_path):
    ffmpeg.input(input_path).output(output_path, vcodec='libx264', acodec='aac').run(overwrite_output=True)

convert_to_web_compatible('routine_frame.mp4', 'routine_frame_fixed.mp4')
