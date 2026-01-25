"""
Chainlit Application - Data Analyst Chat Interface
"""
import os
import tempfile
import uuid
import chainlit as cl
from src.services.data_analyst_agent import run_data_analyst
from src.services.voice_service import get_voice_service
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)


# ===============================
# Chat Settings
# ===============================

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session with settings."""
    try:
        logger.info("Starting chat session")

        # Create settings for model selection
        settings = await cl.ChatSettings([
            cl.input_widget.Select(
                id="model_provider",
                label="Model Provider",
                values=["ollama", "google_genai", "openai", "anthropic", "azure_openai"],
                initial_value="ollama"
            ),
            cl.input_widget.Select(
                id="model_name",
                label="Model Select (Ollama)",
                values=["llama3.1:8b", "llama3.2:1b", "llama3:8b", "deepseek-r1:1.5b", "qwen2.5:7b"],
                initial_value="llama3.1:8b"
            ),
            cl.input_widget.TextInput(
                id="custom_model",
                label="Custom Model Name (Overrides selection if provided)",
                initial="",
                placeholder="e.g., gpt-4o, claude-3-sonnet, gemini-pro"
            )
        ]).send()

        # Combine provider and model name
        provider = settings.get("model_provider", "ollama")
        model = settings.get("custom_model") or settings.get("model_name", "llama3.1:8b")
        full_model_name = f"{provider}:{model}"
        
        # Generate unique thread ID for this session
        thread_id = str(uuid.uuid4())
        
        # Store in session
        cl.user_session.set("model_name", full_model_name)
        cl.user_session.set("thread_id", thread_id)

        # Welcome message
        welcome_message = f"""# Welcome to the Olist Data Analyst! 📊

**Current Model:** `{full_model_name}`

I can help you analyze the Olist E-commerce database. Just ask me questions in natural language!

## What I can do:
- **Query Data**: Ask questions about customers, orders, products, sellers, etc.
- **Create Visualizations**: Request charts, graphs, and trends
- **Provide Insights**: Get key findings and summaries from the data

## Example Questions:
- "How many customers are in the database?"
- "Show me the top 10 cities by number of orders"
- "Create a bar chart of monthly revenue for 2018"
- "What are the most popular product categories?"
- "Compare payment methods used by customers"

## Voice Input:
Click the microphone button to speak your question!

---
*Settings: Click the gear icon to change the model provider.*
"""

        await cl.Message(content=welcome_message).send()
        logger.info(f"Chat session initialized with model: {full_model_name}")

    except Exception as e:
        logger.error(f"Failed to initialize chat session: {str(e)}")
        raise


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings changes."""
    try:
        provider = settings.get("model_provider", "ollama")
        model = settings.get("custom_model") or settings.get("model_name", "llama3.1:8b")
        full_model_name = f"{provider}:{model}"
        cl.user_session.set("model_name", full_model_name)
        
        await cl.Message(content=f"✅ Model updated to: `{full_model_name}`").send()
        logger.info(f"Model updated to: {full_model_name}")
        
    except Exception as e:
        logger.error(f"Failed to update settings: {str(e)}")
        raise


# ===============================
# Message Handler
# ===============================

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages."""
    try:
        model_name = cl.user_session.get("model_name", "ollama:llama3.1:8b")
        thread_id = cl.user_session.get("thread_id", "default")
        
        logger.info(f"Processing message with model: {model_name}")

        # Create response message for streaming
        response_message = cl.Message(content="")
        await response_message.send()

        # Stream the response from the data analyst agent
        async for chunk in run_data_analyst(
            question=message.content,
            model_name=model_name,
            thread_id=thread_id
        ):
            if chunk:
                await response_message.stream_token(chunk)

        await response_message.update()
        logger.info("Message processing completed")

    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        error_message = cl.Message(content=f"❌ Error: {str(e)}")
        await error_message.send()


# ===============================
# Voice Input Handlers
# ===============================

@cl.on_audio_start
async def on_audio_start():
    """Initialize audio buffer when recording starts."""
    cl.user_session.set("audio_buffer", bytearray())
    logger.info("Audio recording session started")
    return True


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    """Handle incoming audio chunks and append to buffer."""
    buffer = cl.user_session.get("audio_buffer")
    if buffer is not None:
        buffer.extend(chunk.data)
        cl.user_session.set("audio_buffer", buffer)
    
    if chunk.isStart:
        cl.user_session.set("audio_mime_type", chunk.mimeType)
        logger.info(f"First audio chunk received, mime type: {chunk.mimeType}")


@cl.on_audio_end
async def on_audio_end():
    """Handle audio recording completion - transcribe and process as message."""
    try:
        # Get the audio buffer
        audio_buffer = cl.user_session.get("audio_buffer")
        mime_type = cl.user_session.get("audio_mime_type", "audio/webm")
        
        if not audio_buffer or len(audio_buffer) == 0:
            await cl.Message(content="❌ No audio received. Please try again.").send()
            return
        
        logger.info(f"Audio recording complete. Size: {len(audio_buffer)} bytes, Type: {mime_type}")
        
        # Save audio to temp file
        if mime_type == "pcm16":
            # For pcm16, wrap in WAV header
            import wave
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_path = f.name
                with wave.open(f.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(audio_buffer)
        else:
            # Determine file extension from mime type
            ext_map = {"webm": ".webm", "wav": ".wav", "mp3": ".mp3"}
            ext = next((v for k, v in ext_map.items() if k in mime_type), ".webm")
            
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(audio_buffer)
                audio_path = f.name
        
        logger.info(f"Saved audio to: {audio_path}")
        
        # Show transcribing message
        transcribing_msg = cl.Message(content="🎤 Transcribing your audio...")
        await transcribing_msg.send()
        
        try:
            # Get voice service and transcribe
            voice_service = get_voice_service(model_size="base")
            transcription = await voice_service.transcribe(audio_path)
            
            if transcription and transcription.strip():
                # Update message to show transcription
                await transcribing_msg.remove()
                await cl.Message(content=f"📝 **You said:** {transcription}").send()
                
                # Process transcription through data analyst
                model_name = cl.user_session.get("model_name", "ollama:llama3.1:8b")
                thread_id = cl.user_session.get("thread_id", "default")
                
                logger.info(f"Processing voice query: {transcription[:100]}...")
                
                # Create response message for streaming
                response_message = cl.Message(content="")
                await response_message.send()

                async for chunk in run_data_analyst(
                    question=transcription,
                    model_name=model_name,
                    thread_id=thread_id
                ):
                    if chunk:
                        await response_message.stream_token(chunk)

                await response_message.update()
                    
            else:
                await transcribing_msg.remove()
                await cl.Message(content="❌ Could not transcribe audio. Please speak clearly and try again.").send()
                
        finally:
            # Cleanup temp file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.info(f"Cleaned up temp audio file: {audio_path}")
        
        # Clear audio buffer
        cl.user_session.set("audio_buffer", None)
        
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        await cl.Message(content=f"❌ Voice processing error: {str(e)}").send()
