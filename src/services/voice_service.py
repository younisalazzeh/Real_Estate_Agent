import os
import tempfile
from pathlib import Path
from typing import Optional
import whisper
from src.logger import setup_application_logger

logger = setup_application_logger(__name__)

# Add FFmpeg to PATH for transcription to work on Windows
def _add_ffmpeg_to_path():
    import glob
    possible_paths = [
        # Common Winget path (recursive search for bin)
        r"C:\Users\Younis AlAzzeh\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\*\bin",
        # Explicit path found earlier
        r"C:\Users\Younis AlAzzeh\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
    ]
    
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            ffmpeg_bin = matches[0]
            if os.path.exists(ffmpeg_bin) and ffmpeg_bin not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + ffmpeg_bin
                logger.info(f"Added FFmpeg to PATH: {ffmpeg_bin}")
                return True
    
    # Check if already in PATH
    import shutil
    if shutil.which("ffmpeg"):
        return True
        
    logger.warning("FFmpeg not found in PATH or common installation locations.")
    return False

_add_ffmpeg_to_path()


class VoiceService:
    """Handles voice-to-text transcription using local Whisper model."""
    
    _instance = None
    _model = None
    
    def __new__(cls, model_size: str = "base"):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize voice service with local Whisper model.
        
        Args:
            model_size: Whisper model size - 'tiny', 'base', 'small', 'medium', 'large'
                       Larger models are more accurate but slower and use more memory.
                       - tiny: ~39M params, fastest, least accurate
                       - base: ~74M params, good balance (recommended)
                       - small: ~244M params, better accuracy
                       - medium: ~769M params, high accuracy
                       - large: ~1550M params, best accuracy, slowest
        """
        if self._initialized:
            return
            
        self.model_size = model_size
        logger.info(f"Loading Whisper model: {model_size}")
        
        try:
            self._model = whisper.load_model(model_size)
            logger.info(f"Whisper model '{model_size}' loaded successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio file to text using local Whisper model.
        
        Args:
            audio_path: Path to the audio file (supports wav, mp3, webm, etc.)
            language: Optional language code (e.g., 'en', 'ar'). Auto-detected if not specified.
            
        Returns:
            Transcribed text or None if transcription failed.
        """
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Transcribe using Whisper
            options = {}
            if language:
                options["language"] = language
            
            result = self._model.transcribe(audio_path, **options)
            
            transcribed_text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            logger.info(f"Transcription complete. Language: {detected_language}, Length: {len(transcribed_text)} chars")
            
            return transcribed_text
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Transcription failed: {str(e)}\n{error_details}")
            return None
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_size": self.model_size,
            "loaded": self._model is not None
        }


# Global singleton instance - will be initialized on first use
def get_voice_service(model_size: str = "base") -> VoiceService:
    """Get or create the voice service singleton."""
    return VoiceService(model_size=model_size)
