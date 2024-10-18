import streamlit as st
import websockets
import asyncio
import json
import os
from pydub import AudioSegment
import base64
import io

# API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# WebSocket URL and headers
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

# Helper function to encode audio to PCM base64
def audio_to_base64(audio_bytes: bytes) -> str:
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data
    return base64.b64encode(pcm_audio).decode()

async def realtime_interaction():
    # Establish WebSocket connection
    async with websockets.connect(WS_URL, extra_headers=HEADERS) as ws:
        st.write("🔊 Connected to Realtime API")

        # Send a welcome message
        welcome_event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Hello!"}]
            }
        }
        await ws.send(json.dumps(welcome_event))

        # Listen for server responses
        async for message in ws:
            response = json.loads(message)
            st.write(response)

            # Handle text/audio responses
            if "content" in response.get("item", {}):
                content = response["item"]["content"]
                if content[0]["type"] == "text":
                    st.write(f"Assistant: {content[0]['text']}")
                elif content[0]["type"] == "audio":
                    audio_data = base64.b64decode(content[0]["audio"])
                    st.audio(audio_data, format="audio/wav")

# Streamlit UI
st.title("🎙️ Realtime Voice-Enabled Chat")
st.write("This demo interacts with the OpenAI Realtime API.")

if st.button("Start Conversation"):
    st.write("🗣️ Conversation started. Speak now...")
    asyncio.run(realtime_interaction())
