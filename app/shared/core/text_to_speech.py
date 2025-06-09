import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import httpx

from app.shared.core.config import settings
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta

RATE_LIMIT = 100  # requests per minute

class TextToSpeechService:
    """Service for text-to-speech conversion using ElevenLabs API."""
    
    def __init__(self):
        # Validate required settings
        self.api_key = settings.ELEVENLABS_API_KEY
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not configured")
            
        self.model_id = settings.ELEVENLABS_MODEL_ID
        if not self.model_id:
            raise RuntimeError("ELEVENLABS_MODEL_ID is not configured")
            
        self.output_format = settings.ELEVENLABS_OUTPUT_FORMAT
        if not self.output_format:
            raise RuntimeError("ELEVENLABS_OUTPUT_FORMAT is not configured")

        # Create cache directory
        self.cache_dir = Path("cache/audio")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize request count tracking
        self.request_count = 0
        self.last_reset = datetime.utcnow()
        
        # Initialize async client
        self.client = httpx.AsyncClient(
            base_url="https://api.elevenlabs.io/v1",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0  # 30 second timeout
        )

    async def generate_audio(self, text: str, voice_id: str = "default") -> str:
        """Generate audio from text using ElevenLabs API."""
        try:
            # Check rate limit
            self._check_rate_limit()
            
            # Check cache first
            cache_key = self._get_cache_key(text, voice_id)
            cache_path = self.cache_dir / f"{cache_key}.{self.output_format}"
            
            if cache_path.exists():
                return str(cache_path)
            
            # Make API request
            response = await self.client.post(
                "/text-to-speech",
                json={
                    "text": text,
                    "model_id": self.model_id,
                    "voice_id": voice_id,
                    "output_format": self.output_format
                }
            )
            response.raise_for_status()
            
            # Save to cache
            cache_path.write_bytes(response.content)
            return str(cache_path)
            
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to generate audio: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices."""
        try:
            response = await self.client.get("/voices")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to get voices: {str(e)}")

    async def get_voice_details(self, voice_id: str) -> Dict[str, Any]:
        """Get details for a specific voice."""
        try:
            response = await self.client.get(f"/voices/{voice_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to get voice details: {str(e)}")

    async def generate_temp_audio(self, text: str, voice_id: str = "default") -> str:
        """Generate temporary audio file and return its path."""
        try:
            audio_path = await self.generate_audio(text, voice_id)
            return audio_path
        except Exception as e:
            raise RuntimeError(f"Failed to generate temporary audio: {str(e)}")

    def _check_rate_limit(self):
        """Check if we've exceeded the rate limit."""
        now = datetime.utcnow()
        if now - self.last_reset > timedelta(minutes=1):
            self.request_count = 0
            self.last_reset = now
            
        if self.request_count >= RATE_LIMIT:
            raise RuntimeError("Rate limit exceeded")
            
        self.request_count += 1

    def _get_cache_key(self, text: str, voice_id: str) -> str:
        """Generate cache key for text and voice combination."""
        key = f"{text}_{voice_id}_{self.model_id}"
        return hashlib.md5(key.encode()).hexdigest()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 