import os
import requests
from pathlib import Path
from fastapi import HTTPException
from app.shared.core.config import settings
import hashlib
import time

class TextToSpeechService:
    """Service for text-to-speech conversion using ElevenLabs API."""
    
    RATE_LIMIT = 100  # Maximum requests per minute
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.model_id = settings.ELEVENLABS_MODEL_ID
        self.output_format = settings.ELEVENLABS_OUTPUT_FORMAT
        self.cache_dir = Path(settings.ELEVENLABS_AUDIO_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._request_counts = {}

    def generate_audio(self, text: str, voice_id: str, client_ip: str) -> bytes:
        """Generate audio from text using ElevenLabs API."""
        if not self._check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        cache_key = self._get_cache_key(text, voice_id)
        cache_path = self.cache_dir / f"{cache_key}.mp3"

        if cache_path.exists():
            return cache_path.read_bytes()

        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": self.api_key},
            json={
                "text": text,
                "model_id": self.model_id,
                "output_format": self.output_format
            }
        )
        response.raise_for_status()

        audio_data = response.content
        cache_path.write_bytes(audio_data)
        return audio_data

    def get_available_voices(self) -> list:
        """Get list of available voices."""
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": self.api_key}
        )
        response.raise_for_status()
        return response.json()["voices"]

    def get_voice_details(self, voice_id: str) -> dict:
        """Get details for a specific voice."""
        response = requests.get(
            f"https://api.elevenlabs.io/v1/voices/{voice_id}",
            headers={"xi-api-key": self.api_key}
        )
        response.raise_for_status()
        return response.json()

    def generate_temp_audio(self, text: str, voice_id: str, client_ip: str) -> str:
        """Generate temporary audio file and return its path."""
        audio_data = self.generate_audio(text, voice_id, client_ip)
        temp_path = f"/tmp/{hashlib.md5(text.encode()).hexdigest()}.mp3"
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        return temp_path

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit."""
        current_time = int(time.time())
        if client_ip not in self._request_counts:
            self._request_counts[client_ip] = []
        
        # Remove requests older than 1 minute
        self._request_counts[client_ip] = [
            t for t in self._request_counts[client_ip]
            if current_time - t < 60
        ]
        
        if len(self._request_counts[client_ip]) >= self.RATE_LIMIT:
            return False
            
        self._request_counts[client_ip].append(current_time)
        return True

    def _get_cache_key(self, text: str, voice_id: str) -> str:
        """Generate cache key for text and voice combination."""
        return hashlib.md5(f"{text}:{voice_id}".encode()).hexdigest() 