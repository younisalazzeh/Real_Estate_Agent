import os
import tempfile
import chainlit as cl
from src.services.nl2sql_agent import nl2sql_agent
from src.services.plotting_agent import plotting_agent
from src.services.voice_service import get_voice_service
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)

# ===============================
# Chat Settings
# ===============================

@cl.on_chat_start
async def on_chat_start():
    try:
        logger.info("Starting chat session")

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
                values=["llama3.1:8b", "llama3.2:1b", "llama3:8b", "deepseek-r1:1.5b"],
                initial_value="llama3.1:8b"
            ),
            cl.input_widget.TextInput(
                id="custom_model",
                label="Custom Model Name (Overrides selection if provided)",
                initial="",
                placeholder="e.g., llama3.1:8b, gpt-4o"
            )
        ]).send()

        # Combine provider and model name
        provider = settings.get("model_provider", "ollama")
        model = settings.get("custom_model") or settings.get("model_name", "llama3.1:8b")
        full_model_name = f"{provider}:{model}"
        cl.user_session.set("model_name", full_model_name)
        cl.user_session.set("message_history", [])
        cl.user_session.set("active_agent", "sql")
        cl.user_session.set("original_question", "") # Store for trend analysis

        await cl.context.emitter.set_commands(COMMANDS)

        welcome_message = f"""Welcome to the **Real Estate Assistant**! 🏠

**🤖 Current Model:** {full_model_name}

I have two specialized agents to help you:

**🔷 SQL Agent** (default)
- Query and analyze real estate data using natural language
- Execute SQL queries against the database
- Automatically create visualizations when appropriate

**📊 Plotting Agent**
- Generate custom Plotly visualizations
- Create charts from data or descriptions
- Support multiple chart types (bar, line, scatter, pie, histogram, etc.)

**🎤 Voice Input**
- Click the microphone button to speak your query
- Your speech will be transcribed automatically

**⚙️ Settings**
- Click the settings icon to change the model provider
- Supports: Ollama (local), Google, OpenAI, Anthropic, Azure

**Example queries:**
- "Show me the top 10 cities by number of customers"
- "Create a bar chart showing monthly sales trends"

Current mode: **SQL Agent** 🔷"""

        await cl.Message(content=welcome_message).send()
        logger.info(f"Chat session initialized with model: {settings.get('model_name')}")

    except Exception as e:
        logger.error(f"Failed to initialize chat session: {str(e)}")
        raise

@cl.on_settings_update
async def on_settings_update(settings):
    try:
        provider = settings.get("model_provider", "ollama")
        model = settings.get("custom_model") or settings.get("model_name", "llama3.1:8b")
        full_model_name = f"{provider}:{model}"
        cl.user_session.set("model_name", full_model_name)
        logger.info(f"Model updated to: {full_model_name}")
        
    except Exception as e:
        logger.error(f"Failed to update settings: {str(e)}")
        raise

# ===============================
# Command Definitions
# ===============================

COMMANDS = [
    {
        "id": "sql",
        "icon": "database",
        "description": "SQL Agent - Query the database with natural language",
        "persistent": True
    },
    {
        "id": "plot",
        "icon": "bar-chart-3",
        "description": "Plotting Agent - Create custom visualizations",
        "persistent": True
    }
]

# ===============================
# NL2SQL Agent Integration
# ===============================

async def run_nl2sql_agent_with_steps(question: str, model_name: str):
    message_history = cl.user_session.get("message_history", [])

    response_message = cl.Message(content="")
    await response_message.send()

    async for chunk in nl2sql_agent(question, model_name, message_history):
        if isinstance(chunk, dict):
            if chunk.get("type") == "tool_call":
                async with cl.Step(name="execute_sql", type="tool", show_input="sql") as step:
                    step.input = chunk.get("query", "")
                    step.output = chunk.get("result", "")

            elif chunk.get("type") == "memory":
                cl.user_session.set("message_history", chunk.get("messages", []))

            elif chunk.get("type") == "warning":
                await response_message.stream_token(f"\n\n[{chunk.get('content')}]")

        elif isinstance(chunk, str):
            await response_message.stream_token(chunk)

    await response_message.update()

# ===============================
# Plotting Agent Integration
# ===============================

async def run_plotting_agent_with_steps(question: str, model_name: str):
    message_history = cl.user_session.get("message_history", [])

    response_message = cl.Message(content="")
    await response_message.send()

    async for chunk in plotting_agent(question, model_name=model_name, message_history=message_history):
        if isinstance(chunk, dict):
            if chunk.get("type") == "visualization":
                if chunk.get("status") == "error":
                    await response_message.stream_token(f"\n\n⚠️ Visualization error: {chunk.get('message', 'Unknown error')}")

            elif chunk.get("type") == "memory":
                cl.user_session.set("message_history", chunk.get("messages", []))

        elif isinstance(chunk, str):
            await response_message.stream_token(chunk)

    await response_message.update()

# ===============================
# Message Handler
# ===============================

@cl.on_message
async def on_message(message: cl.Message):
    try:
        model_name = cl.user_session.get("model_name", "google_genai:gemini-3-flash-preview")

        if message.command:
            if message.command == "sql":
                cl.user_session.set("active_agent", "sql")
                logger.info("Switched to SQL Agent mode via command")
                await cl.Message(
                    content="**Mode switched to SQL Agent 🔷**\n\nI'll help you query the database using natural language."
                ).send()
                return
            elif message.command == "plot":
                cl.user_session.set("active_agent", "plot")
                logger.info("Switched to Plotting Agent mode via command")
                await cl.Message(
                    content="**Mode switched to Plotting Agent 📊**\n\nI'll help you create custom visualizations. You can provide data context or describe the chart you want."
                ).send()
                return

        active_agent = cl.user_session.get("active_agent", "sql")
        logger.info(f"Processing message with model: {model_name}, active_agent: {active_agent}")

        if active_agent == "sql":
            await run_nl2sql_agent_with_steps(message.content, model_name)
        elif active_agent == "plot":
            await run_plotting_agent_with_steps(message.content, model_name)
        else:
            logger.warning(f"Unknown agent type: {active_agent}, defaulting to SQL")
            await run_nl2sql_agent_with_steps(message.content, model_name)

        logger.info("Message processing completed")

    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        error_message = cl.Message(content=f"Error: {str(e)}")
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
            # For pcm16, we need to wrap it in a WAV header
            import wave
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_path = f.name
                # Chainlit default for pcm16 is usually 16kHz or 44.1kHz. 
                # According to config.toml, it's set to 24000.
                with wave.open(f.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(24000) 
                    wav_file.writeframes(audio_buffer)
        else:
            # Determine file extension from mime type
            if "webm" in mime_type:
                ext = ".webm"
            elif "wav" in mime_type:
                ext = ".wav"
            elif "mp3" in mime_type:
                ext = ".mp3"
            else:
                ext = ".webm"
            
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
                
                # Process transcription as regular message
                model_name = cl.user_session.get("model_name", "ollama:llama3.2:1b")
                active_agent = cl.user_session.get("active_agent", "sql")
                
                logger.info(f"Processing voice query: {transcription[:100]}...")
                
                if active_agent == "sql":
                    await run_nl2sql_agent_with_steps(transcription, model_name)
                elif active_agent == "plot":
                    await run_plotting_agent_with_steps(transcription, model_name)
                else:
                    await run_nl2sql_agent_with_steps(transcription, model_name)
                    
            else:
                await transcribing_msg.remove()
                await cl.Message(content="❌ Could not transcribe audio. Please speak clearly and try again.").send()
                
        finally:
            # Cleanup temp file
            import os
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.info(f"Cleaned up temp audio file: {audio_path}")
        
        # Clear audio buffer
        cl.user_session.set("audio_buffer", None)
        
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        await cl.Message(content=f"❌ Voice processing error: {str(e)}").send()
