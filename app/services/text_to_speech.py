from typing import Optional, Union, Dict
import requests
import os
from pathlib import Path
import logging
from app.shared.core.config import settings
import tempfile
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.core.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

class TextToSpeechService:
    """Service for generating text-to-speech audio using ElevenLabs API."""
    
    BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"
    CACHE_EXPIRY = timedelta(days=7)  # Cache audio files for 7 days
    RATE_LIMIT = 50  # Requests per minute
    RATE_WINDOW = 60  # Seconds
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.model_id = settings.ELEVENLABS_MODEL_ID
        self.output_format = settings.ELEVENLABS_OUTPUT_FORMAT
        self.cache_dir = Path(settings.ELEVENLABS_AUDIO_CACHE_DIR)
        self.headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=self.RATE_LIMIT,
            window_seconds=self.RATE_WINDOW
        )
    
    def _get_cache_path(self, text: str, voice_id: str) -> Path:
        """Generate cache file path based on text and voice."""
        # Create a hash of the text and voice_id to use as filename
        content_hash = hashlib.md5(f"{text}:{voice_id}".encode()).hexdigest()
        return self.cache_dir / f"{content_hash}.mp3"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached file exists and is not expired."""
        if not cache_path.exists():
            return False
        
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < self.CACHE_EXPIRY
    
    def _log_audio_generation(self, text: str, voice_id: str, cache_hit: bool, success: bool, error: Optional[str] = None):
        """Log audio generation events."""
        log_data = {
            "event": "tts_audio_generation",
            "text_length": len(text),
            "voice_id": voice_id,
            "cache_hit": cache_hit,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        if error:
            log_data["error"] = str(error)
        
        if success:
            logger.info("TTS audio generation successful", extra=log_data)
        else:
            logger.error("TTS audio generation failed", extra=log_data)
    
    def generate_audio(
        self,
        text: str,
        voice_id: str,
        model_id: Optional[str] = None,
        output_format: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
        use_cache: bool = True,
        client_ip: Optional[str] = None
    ) -> Union[bytes, str]:
        """
        Generate TTS audio from text using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: Model to use for generation (defaults to settings)
            output_format: Audio output format (defaults to settings)
            save_path: Optional path to save the audio file
            use_cache: Whether to use cached audio if available
            client_ip: Client IP for rate limiting
            
        Returns:
            If save_path is None: Audio data as bytes
            If save_path is provided: Path to saved audio file
        """
        # Check rate limit if client IP is provided
        if client_ip and not self.rate_limiter.check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        try:
            # Check cache first if enabled
            if use_cache:
                cache_path = self._get_cache_path(text, voice_id)
                if self._is_cache_valid(cache_path):
                    logger.info(f"Using cached audio file: {cache_path}")
                    if save_path:
                        # Copy cached file to save_path
                        import shutil
                        shutil.copy2(cache_path, save_path)
                        self._log_audio_generation(text, voice_id, True, True)
                        return str(save_path)
                    self._log_audio_generation(text, voice_id, True, True)
                    return cache_path.read_bytes()
            
            url = f"{self.BASE_URL}/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": model_id or self.model_id,
                "output_format": output_format or self.output_format
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            audio_data = response.content
            
            # Save to cache if enabled
            if use_cache:
                cache_path = self._get_cache_path(text, voice_id)
                cache_path.write_bytes(audio_data)
                logger.info(f"Cached audio file: {cache_path}")
            
            if save_path:
                # Create directory if it doesn't exist
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save audio file
                with open(save_path, "wb") as f:
                    f.write(audio_data)
                self._log_audio_generation(text, voice_id, False, True)
                return str(save_path)
            
            self._log_audio_generation(text, voice_id, False, True)
            return audio_data
            
        except requests.exceptions.RequestException as e:
            self._log_audio_generation(text, voice_id, False, False, str(e))
            logger.error(f"Error generating TTS audio: {str(e)}", exc_info=True)
            raise
    
    def generate_temp_audio(
        self,
        text: str,
        voice_id: str,
        use_cache: bool = True,
        client_ip: Optional[str] = None
    ) -> str:
        """
        Generate TTS audio and save to a temporary file.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            use_cache: Whether to use cached audio if available
            client_ip: Client IP for rate limiting
            
        Returns:
            Path to temporary audio file
        """
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / f"tts_{uuid.uuid4()}.mp3"
        
        return self.generate_audio(
            text,
            voice_id,
            save_path=temp_file,
            use_cache=use_cache,
            client_ip=client_ip
        )
    
    def get_available_voices(self) -> list:
        """Get list of available voices from ElevenLabs."""
        try:
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["voices"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching available voices: {str(e)}", exc_info=True)
            raise
    
    def get_voice_details(self, voice_id: str) -> Dict:
        """Get detailed information about a specific voice."""
        try:
            response = requests.get(
                f"https://api.elevenlabs.io/v1/voices/{voice_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching voice details: {str(e)}", exc_info=True)
            raise

# Create singleton instance
tts_service = TextToSpeechService() 