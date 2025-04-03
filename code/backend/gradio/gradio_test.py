import gradio as gr
import os
from queryOllama import queryOllama

VIDEO_DIR = "uploaded_videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# Function to process text input and maintain chat history
def process_input(text, chat_history):
    response = queryOllama(text)

    # Append new input and response to chat history
    chat_history.append((text, response))

    return "", chat_history  # Clear text input and update chatbot

# Function to save uploaded videos
def save_video(video):
    if video is not None:
        video_path = os.path.join(VIDEO_DIR, video.name)
        with open(video_path, "wb") as f:
            f.write(video.read())
    return update_video_gallery()

# Function to get video library
def update_video_gallery():
    return [os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR)]

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Enhanced Gradio App with Chat History & Video Support")

    chat_history = gr.State([])  # Keeps track of messages

    with gr.Row():
        text_input = gr.Textbox(label="Enter text", interactive=True)
        submit_button = gr.Button("Submit")

    chat_output = gr.Chatbot(label="Chat History")

    submit_button.click(
        process_input,
        inputs=[text_input, chat_history],
        outputs=[text_input, chat_output]  # Updates chatbot instead of input field
    )

    # Video Upload Section
    gr.Markdown("### Upload and View Videos")
    video_input = gr.Video(label="Upload a video")
    video_gallery = gr.Gallery(value=update_video_gallery(), label="Video Library")

    video_input.upload(save_video, inputs=video_input, outputs=video_gallery)

demo.launch()
